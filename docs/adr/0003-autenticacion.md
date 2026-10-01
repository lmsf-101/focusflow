# ADR-0003: Autenticación

- **Estado:** Propuesto
- **Fecha:** 2026-10-01

## Contexto

FocusFlow es una aplicación que busca albergar múltiples usuarios: cada uno tiene sus propios proyectos, categorías, etiquetas y tareas, y ningún usuario debe poder ver ni modificar los datos de otro. Eso exige:
- Autenticación: Identificar quién hace cada petición
- Autorización: Decidir qué puede hacer con cada recurso

Restricciones para MVP:

- Proyecto individual, con el aprendizaje y la simplicidad por delante del rendimiento y de la cobertura funcional.
- **No hay infraestructura de correo** ni intención de montarla en el MVP. Eso descarta de entrada la verificación de email, el "olvidé mi contraseña" y cualquier mitigación que dependa de enviar un mensaje.
- El frontend (Semana 3) será una SPA de React servida desde un origen distinto al de la API, por lo que el mecanismo de autenticación tiene que funcionar entre orígenes.
- El destino de despliegue es AWS, mediante el uso de ECS Fargate detrás de un ALB, potencialmente con más de una instancia de la aplicación. En base a ello, el manejo de estado de sesión en memoria del proceso no aplica aquí.

## Decisión

- **Hashing de contraseñas: Argon2 vía `pwdlib`**, usando `PasswordHash.recommended()`. Argon2id es la recomendación actual de OWASP para contraseñas nuevas. Se usa `pwdlib` en vez de `passlib` porque passlib no se mantiene desde el 2020 y arrastra incompatibilidades con Python moderno; `pwdlib` es el sucesor recomendado.
- **Autenticación por JWT con el flujo OAuth2 password** (`OAuth2PasswordRequestForm` + `OAuth2PasswordBearer`). `POST /token` recibe credenciales como `form-data` y devuelve un *bearer token*; el cliente lo manda en la cabecera `Authorization: Bearer <token>` en cada petición.
- **Token firmado con HS256** (simétrico), con el `secret_key` de la configuración. El payload lleva solo `sub` (el `id` del usuario, como string) y `exp`.
- **Expiración corta y sin *refresh token***. `access_token_expire_minutes` es un ajuste **obligatorio sin valor por defecto** en `config.py`, para que un despliegue mal configurado falle al arrancar en vez de elegir por su cuenta una expiración insegura.
- **Verificación con lista explícita de algoritmos**: `jwt.decode(..., algorithms=[settings.algorithm])`. Pasar la lista explícita es lo que evita los ataques de confusión de algoritmo (un token con `alg: none` o con HMAC cuando se espera RSA).
- **Autorización por dependencia, no por comprobación dentro del handler.** `get_current_user` resuelve la identidad; `get_owned_project` resuelve identidad **y** propiedad en una sola consulta. El handler recibe un objeto que ya es del usuario; no puede olvidarse de comprobarlo porque nunca llega a tener en la mano uno ajeno.
- **Recurso ajeno → 404, no 403.** Un 403 confirmaría que el recurso existe y que es de alguien más. El 404 no distingue "no existe" de "no es tuyo", y así la API no funciona como **oráculo de existencia**.
- **401 con un `detail` genérico**. Los tres caminos de fallo de `get_current_user` (token ilegible, sin `sub`, usuario inexistente) devuelven el mismo mensaje `"Unauthorized"`, para no filtrar en qué paso falló la validación.

## Alternativas consideradas

- **Sesiones en servidor con cookie de sesión:** Es más fácil de revocar (borras la sesión y se acabó) y lo que elegiría una app con frontend servido desde el mismo origen. Se descarta porque exige almacén de sesiones compartido entre instancias de Fargate (Redis o la base de datos), que es infraestructura extra y una decisión más que sostener. Con JWT el servidor no guarda nada.
- **JWT en cookie `HttpOnly` + `Secure` + `SameSite`:** Es más seguro que guardar el token en `localStorage`, porque JavaScript no puede leerlo y eso neutraliza el robo del token por XSS. El precio es tener que defenderse de CSRF (token anti-CSRF o `SameSite=Strict`) y lidiar con cookies entre orígenes distintos. **Queda como decisión abierta**, no como descarte.
- **Access token + refresh token:** Es el estándar cuando quieres expiración corta *y* sesiones largas sin re-login. Añade un endpoint `/refresh`, almacenamiento y rotación de los refresh tokens, y detección de reuso. Para un MVP de un usuario de demo no compensa; la consecuencia aceptada es que la sesión caduca y hay que volver a loguearse.
- **Proveedor de identidad externo (Auth0, AWS Cognito, "login con Google"):** Es lo que probablemente usaría un proyecto real, y elimina de golpe el hashing, la enumeración de usuarios y el "olvidé mi contraseña". Se descarta **por motivo de aprendizaje**: construir e instrumentar el flujo a mano para entender bien los conceptos relevantes. Además, ataría el proyecto a una cuenta de un tercero.
- **RS256 (firma asimétrica) en vez de HS256:** Útil cuando varios servicios verifican tokens que solo uno emite (el verificador necesita la clave pública, no la de firma). Aquí emite y verifica el mismo proceso, así que la asimetría no compra nada y sí añade manejo de un par de claves.
- **bcrypt en vez de Argon2:** Sigue siendo aceptable según OWASP y está más extendido, pero tiene el límite histórico de 72 bytes de entrada y Argon2id es la recomendación preferente para desarrollos nuevos.

## Limitaciones conocidas

1. **Enumeración de usuarios en `POST /register`.** El endpoint devuelve 409 con un mensaje `"The email has been registered previously..."`, lo que permite a cualquiera averiguar si un email está registrado. Mitigarlo de verdad exige responder siempre 202 y mandar la información por un canal distinto, como correo. Para el MVP, **se acepta conscientemente**: el mensaje claro vale más aquí que la opacidad, porque sin recuperación de cuenta, un usuario que no sabe que ya está registrado se queda bloqueado.

2. **Oráculo de tiempo en `POST /token`.** La condición `if not (user and verify_password(...))` hace cortocircuito: si el email no existe, Argon2 no se ejecuta y la respuesta vuelve en una fracción del tiempo. Midiendo latencias se distingue "email desconocido" de "contraseña incorrecta", pese a que el 401 es idéntico en ambos casos. La mitigación estándar es considerar un hash señuelo (cálculo para una entrada falsa) cuando el usuario no existe, para que el coste de CPU sea el mismo por los dos caminos.

3. **Un token válido no se puede revocar.** Es el precio del diseño sin estado: no hay lista de revocación, así que un token robado sirve hasta su `exp`, y el "logout" solo puede ser que el cliente lo tire. La expiración corta es la única mitigación. Cambiar la contraseña tampoco invalida los tokens ya emitidos.

4. **Sin límite de intentos ni bloqueo de cuenta.** `POST /token` admite peticiones ilimitadas, lo que puede verse afectado por un ataque de fuerza bruta o de *credential stuffing* más allá del coste de Argon2. El *rate limiting* está pendiente, para cuando haya una opción de infraestructura donde ponerlo (ALB), no en el handler.

5. **El `secret_key` firma y verifica.** Al ser HS256 simétrico, quien obtenga ese valor puede **forjar** tokens de cualquier usuario, no solo leerlos. Al desplegar debe venir de un gestor de secretos (Secrets Manager o SSM Parameter Store en AWS), nunca de una variable de entorno escrita en la definición de la tarea. Rotarlo invalida todos los tokens en circulación.

## Consecuencias

- La API es **sin estado** en lo que respecta a autenticación: cualquier instancia detrás del ALB puede atender cualquier petición sin almacén compartido.
- `PasswordHash.recommended()` delega la elección del algoritmo a `pwdlib`. A favor: los parámetros siguen a la recomendación del ecosistema sin que haya que vigilarlos. En contra: **el algoritmo o sus parámetros pueden cambiar en una subida de dependencia**, y no se controla el coste en memoria ni las iteraciones.
- El patrón `get_owned_project` **se repetirá** por cada recurso con dueño (`tasks`, `categories`, `tags`). El refactor a una fábrica genérica `owned(Model)` queda condicionado a la regla de tres y a comprobar que `Task` encaja en el molde.
- Las pruebas de autorización son **tests de integración, no unitarios**: lo que se verifica es que la consulta filtra, y eso solo se ve con base de datos. De ahí que los tests de aislamiento de `projects` monten dos usuarios reales y comprueben los dos caminos.
- Queda una decisión pendiente: **dónde guarda el token el frontend** (memoria, `localStorage` o cookie `HttpOnly`). La elección cambia el modelo de amenaza del lado del cliente —XSS frente a CSRF— y, si se va a cookie, obliga a revisar esta decisión.

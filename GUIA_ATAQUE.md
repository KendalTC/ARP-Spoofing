# 🎯 Guía paso a paso del ataque ARP Spoofing

Guía práctica para **ejecutar y explicar** la demostración. Está separada por máquina (🖥️ Host, 🐉 Atacante, 🐧 Víctima) y cada comando incluye **qué hace** y **cómo explicarlo**.

> ⚠️ Solo para el laboratorio aislado, con equipos y credenciales propios/ficticios. Nunca sobre redes ajenas.

---

## 🧠 La idea en una frase

Normalmente la víctima habla con el gateway (el "portón" de la red) para salir. Con **ARP Spoofing**, el atacante engaña a la víctima haciéndole creer que **él es el gateway**, así todo el tráfico de la víctima pasa primero por el atacante (*Man-in-the-Middle*). Si ese tráfico va **sin cifrar (HTTP)**, el atacante ve usuarios y contraseñas en texto plano.

## 🗺️ Mapa de red

| Máquina | Rol | IP | MAC (de este lab) |
|---|---|---|---|
| 🖥️ PC Windows (host) | Servidor / gateway | `192.168.56.1` | `0a:00:27:00:00:11` |
| 🐉 Kali Linux (VM) | Atacante | `192.168.56.10` | `08:00:27:5a:87:bc` |
| 🐧 Lubuntu (VM) | Víctima | `192.168.56.20` | — |

> Antes de empezar: las **dos VMs encendidas** y el host disponible. Verificá con un `ping 192.168.56.1` desde la víctima.

---

## PASO 0 · 🖥️ HOST (Windows) — Levantar el sitio de login falso

En una terminal (CMD), en la carpeta donde está el script:

```bash
python servidor_falso.py
```

**¿Qué hace?** Levanta un servidor web en `http://192.168.56.1` (puerto 80) que muestra un formulario de inicio de sesión. Es el "sitio corporativo" al que la víctima se va a conectar.
**Cómo explicarlo:** "Este es el servidor interno de la empresa; la víctima entrará aquí a iniciar sesión."

✅ Debe quedar diciendo *"Servidor falso en http://192.168.56.1"*. **No cierres esa ventana.**

---

## PASO 1 · 🐧 VÍCTIMA (Lubuntu) — Tomar la línea base (el "ANTES")

```bash
ip neigh
```

**¿Qué hace?** Muestra la tabla ARP de la víctima: qué dirección MAC tiene asociada cada IP. Fijate en el `192.168.56.1` → tiene su **MAC real** (`0a:00:27:00:00:11`).
**Cómo explicarlo:** "Así se ve la red sana: la víctima sabe cuál es el MAC verdadero del gateway." 📸 *Capturá esta pantalla.*

---

## PASO 2 · 🐉 ATACANTE (Kali) — Activar el reenvío de paquetes

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

**¿Qué hace?** Le dice a Kali que **reenvíe** hacia el gateway todo el tráfico que reciba de la víctima. Así la víctima sigue navegando con normalidad y **no nota nada**.
**Cómo explicarlo:** "Esto hace el ataque invisible: la víctima no pierde internet, solo que ahora pasa por mí."

---

## PASO 3 · 🐉 ATACANTE (Kali) — Lanzar el ARP Spoofing

```bash
sudo ettercap -T -i eth0 -M arp:remote /192.168.56.20// /192.168.56.1//
```

**¿Qué hace?** Inicia **ettercap** y envenena las tablas ARP:
- `-T` → modo texto (consola).
- `-i eth0` → usa la interfaz de red del laboratorio.
- `-M arp:remote` → activa el ataque *Man-in-the-Middle* por ARP con reenvío.
- `/192.168.56.20//` → objetivo 1: la **víctima**.
- `/192.168.56.1//` → objetivo 2: el **gateway/host**.

Kali le dice a la víctima "yo soy el gateway" y al gateway "yo soy la víctima", quedando **en medio** de ambos.
**Cómo explicarlo:** "Con un comando me meto entre la víctima y el gateway; desde ahora todo su tráfico pasa por mí." **Dejá esta terminal abierta.**

---

## PASO 4 · 🐧 VÍCTIMA (Lubuntu) — Verificar el engaño (el "DESPUÉS")

```bash
ip neigh
```

**¿Qué hace?** Vuelve a mostrar la tabla ARP. Ahora el `192.168.56.1` aparece con el **MAC de Kali** (`08:00:27:5a:87:bc`) en lugar de su MAC real.
**Cómo explicarlo:** "La víctima ahora cree que Kali es el gateway. Ese cambio de MAC es la prueba del Man-in-the-Middle." 📸 *Capturá esta pantalla y compará con la del Paso 1.*

---

## PASO 5 · 🐉 ATACANTE (Kali) — Capturar el tráfico con Wireshark

En **otra terminal** de Kali (no cierres ettercap):

```bash
sudo wireshark
```

Dentro de Wireshark:
1. Doble clic en la interfaz **eth0** para iniciar la captura.
2. En la barra de filtro escribí `http` y Enter.

**¿Qué hace?** Captura en vivo todos los paquetes que pasan por Kali. El filtro `http` deja ver solo el tráfico web (sin cifrar).
**Cómo explicarlo:** "Aquí veo en tiempo real el tráfico de la víctima que pasa por mí."

---

## PASO 6 · 🐧 VÍCTIMA (Lubuntu) — Iniciar sesión (disparar la captura)

En Firefox:
1. Entrá a `http://192.168.56.1`
2. Usuario: `empleado1`  ·  Contraseña: `Secreta123`  → **Ingresar**

**¿Qué hace?** La víctima envía sus credenciales al "servidor". Como viajan por **HTTP (sin cifrar)**, pasan en texto plano a través de Kali.
**Cómo explicarlo:** "La víctima hace algo totalmente normal: iniciar sesión. No sabe que yo lo estoy viendo."

---

## PASO 7 · 🐉 ATACANTE (Kali) — Leer las credenciales robadas 🎯

En Wireshark:
1. Buscá el paquete **`POST /login`**.
2. Clic derecho → **Follow → HTTP Stream**.

**¿Qué hace?** Reconstruye la conversación completa de ese login. En el cuerpo vas a ver:

```
usuario=empleado1&clave=Secreta123
```

**Cómo explicarlo:** "Aquí está el momento clave: el usuario y la contraseña, legibles. Si esto fuera un banco o un correo corporativo, ya los tendría." 📸 *Capturá esta pantalla.*

> 💡 Bonus: ettercap también suele imprimir las credenciales en su propia terminal.

---

## PASO 8 · 🐉 ATACANTE (Kali) — Guardar evidencia y limpiar

**Guardar la captura:** en Wireshark → **File → Save As** → `captura_arp.pcap` (formato pcap).
**¿Qué hace?** Guarda toda la captura para analizarla después (p. ej. en NetworkMiner) y como evidencia.

**Detener el ataque:** en la terminal de **ettercap**, presioná la tecla:

```
q
```

**¿Qué hace?** Detiene el envenenamiento y **restaura las tablas ARP** reales. La red vuelve a la normalidad.
**Cómo explicarlo:** "Cierro el ataque de forma limpia; la red queda como estaba. Esto también muestra responsabilidad en la prueba."

---

## 🛡️ Cierre: ¿cómo se defiende una empresa?

Mencioná estas contramedidas al final (el objetivo real es **defender**):

| Defensa | Qué hace |
|---|---|
| **HTTPS / cifrado** | Aunque intercepten el tráfico, va cifrado e ilegible. |
| **Dynamic ARP Inspection (DAI)** | El switch valida los mensajes ARP y bloquea los falsos. |
| **Port Security** | Limita qué dispositivos/MAC pueden conectarse por puerto. |
| **VLANs (segmentación)** | Reduce el alcance de un atacante dentro de la red. |
| **VPN** | Cifra todo el tráfico de punta a punta. |
| **Monitoreo de red** | Detecta el comportamiento anómalo del envenenamiento ARP. |

---

## 🔁 Resumen rápido (chuleta)

| # | Máquina | Comando / acción |
|---|---|---|
| 0 | 🖥️ Host | `python servidor_falso.py` |
| 1 | 🐧 Víctima | `ip neigh`  *(línea base)* |
| 2 | 🐉 Kali | `sudo sysctl -w net.ipv4.ip_forward=1` |
| 3 | 🐉 Kali | `sudo ettercap -T -i eth0 -M arp:remote /192.168.56.20// /192.168.56.1//` |
| 4 | 🐧 Víctima | `ip neigh`  *(MAC cambiado)* |
| 5 | 🐉 Kali | `sudo wireshark`  → eth0 → filtro `http` |
| 6 | 🐧 Víctima | Firefox → `http://192.168.56.1` → login |
| 7 | 🐉 Kali | Wireshark → `POST /login` → Follow HTTP Stream |
| 8 | 🐉 Kali | Guardar `.pcap` + `q` en ettercap |

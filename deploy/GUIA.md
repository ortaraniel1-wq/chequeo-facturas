# Acceso desde fuera: VPS + WireGuard + Caddy

```
Celular (PWA) --HTTPS--> VPS (Caddy) --WireGuard--> Servidor Profit (API :8000)
```
El servidor de Profit inicia el túnel hacia el VPS, así que no se abre ningún puerto en la tienda.

## 0. DNS
Crear un registro **A**: `api.TUDOMINIO.com` -> IP pública del VPS.

## 1. VPS (Ubuntu)
```bash
sudo apt update && sudo apt install -y wireguard ufw
wg genkey | sudo tee /etc/wireguard/vps.key | wg pubkey | sudo tee /etc/wireguard/vps.pub
sudo chmod 600 /etc/wireguard/vps.key
```
Copiar `deploy/wg0-vps.conf` a `/etc/wireguard/wg0.conf` y completar las claves
(la pública del servidor Profit se genera en el paso 2).
```bash
sudo systemctl enable --now wg-quick@wg0
sudo ufw allow OpenSSH && sudo ufw allow 51820/udp && sudo ufw allow 80,443/tcp && sudo ufw enable
```
Instalar Caddy siguiendo https://caddyserver.com/docs/install#debian-ubuntu-raspbian
y copiar `deploy/Caddyfile` a `/etc/caddy/Caddyfile`:
```bash
sudo systemctl reload caddy
```

## 2. Servidor Profit (Windows)
1. Instalar WireGuard para Windows (wireguard.com/install).
2. "Añadir túnel > Añadir túnel vacío": genera el par de claves. Pasar la **pública** al VPS.
3. Pegar el contenido de `deploy/wg0-profit-windows.conf` (con las claves) y activar.
4. Arrancar la API escuchando solo en la IP del túnel:
   `uvicorn main:app --host 10.8.0.2 --port 8000`
5. Instalar WireGuard como servicio (la app lo hace con "Instalar servicio de túnel") y la API como servicio para que arranquen con Windows.

## 3. Probar
- Desde el VPS: `curl http://10.8.0.2:8000/salud`
- Desde cualquier lado: `curl https://api.TUDOMINIO.com/salud`
- `curl -H "X-Token: TU_TOKEN" https://api.TUDOMINIO.com/factura/12345`

En `api/.env`, poner `CORS_ORIGINS` con el origen de la PWA.

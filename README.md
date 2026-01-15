## Maratonda kullanılan araçlar

[Tugay Aloğlu](https://www.youtube.com/c/TugayAlo%C4%9Flu) tarafından yapılan maratonda kullanılması için kodlanan YouTube, Bynogame ve Oyunfor destekli sayaç ve diğer bazı araçların kaynak kodlarıdır. Sayaç, bağış tablosu ve bağış hedef barı sağlar.

### Gereken erişim anahtarları (.env)

-   `QUART_SECRET_KEY`: Quart uygulaması için rastgele bir gizli anahtar.
-   `STREAMLABS_SOCKET_TOKEN`: Bağışları canlı takip edebilmek için Streamlabs soket tokeni.
-   `YOUTUBE_API_KEY`: YouTube'dan gelen bağışlarda kanal adını çekebilmek için gerekli API anahtarı.

### Gerekli Python Kütüphaneleri

```
aiohttp
aiosqlite
python-dotenv
python-socketio
quart
quart-auth
```

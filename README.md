## Maratonda kullanılan araçlar

[Tugay Aloğlu](https://www.youtube.com/c/TugayAlo%C4%9Flu) tarafından yapılan maratonda kullanılması için kodlanan YouTube, Bynogame ve Oyunfor destekli sayaç ve diğer bazı araçların kaynak kodlarıdır.

Streamlabs soket tokeninin `.env` dosyasında `STREAMLABS_SOCKET_TOKEN` olarak tanımlanması gerekmektedir.

### Örnek config.json dosyası
```json
{
    "end-date": "2024-10-19T20:00:00.000000",
    "pause-date": null
}
```

### Gerekli Python Kütüphaneleri
```
aiohttp
orjson
python-dotenv
python-socketio
quart
quart-auth
```
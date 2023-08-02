"""
    run_mode运行方式 debug/release
"""
settings = {
    "run_mode": "debug",
    "secret_key": "R7gKOqXTiti9HuXG",
    "app_jwt_expire": 30 * 24 * 3600,
    "admin_jwt_expire": 24 * 3600,
    "SAVE_URL": "/usr/local/var/www/static",
    "SITE_URL": "http://localhost:8080/static",
    "BACKUP_URL": "/usr/local/var/backups",
    'redis': {
        "host": "127.0.0.1",
        "port": 6379,
        "password": "123456"
    },
    'mongo': {
        "host": "127.0.0.1",
        "port": 27017,
        "database": "base-db"
    }
}

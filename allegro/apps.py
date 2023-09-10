from django.apps import AppConfig


class AllegroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "allegro"

    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from . import platform_senders
        scheduler = BackgroundScheduler()
        scheduler.add_job(platform_senders.refresh_tokens_every_4_hours, 'interval', hours=4)
        scheduler.add_job(platform_senders.check_time_of_invalidation, 'interval', seconds=1)
        scheduler.add_job(platform_senders.check_quants_every_5_seconds, 'interval', seconds=5)
        scheduler.start()

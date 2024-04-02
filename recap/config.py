from environs import Env

# a class to load configurations for development, staging, and produciton cleanly
env = Env()
env.read_env()

class RecapConfig:
    RECAP_LogLevel=env.str("RECAP_LogLevel")
    RECAP_AI_API_URL=env.str("RECAP_AI_API_URL")
    RECAP_REDIS_URL=env.str("RECAP_REDIS_URL")
    RECAP_RQ_QUEUE=env.str("RECAP_RQ_QUEUE")
    RECAP_SECRET_KEY=env.str("RECAP_SECRET_KEY")

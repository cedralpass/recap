# Background Jobs

OpenAI apis are time consuming, for example ChatGPT4 takes ~14 seconds for prompts powering recap.  We will use a simple background job processor: [python-rq]([https://python-rq.org/])

This requires redis to be installed

## Redis Installation on Mac
to install redis, reccomend using homebrew
```brew install redis```

Then you have several ways to start it locally:

### Configure using
```/opt/homebrew/etc/redis.conf```

### As a service: 
```brew services start redis```
### In terminal

```/opt/homebrew/opt/redis/bin/redis-server```




import httpx

class AiApiHelper:
    @staticmethod
    def ClassifyUrl(url, reference):
         request_data = {'url': url, 'ref_key': reference, 'secret':"abc123"}

         r = httpx.post('http://recapa-farga-l9gassm1meed-42ef6e85215dea14.elb.us-west-2.amazonaws.com/classify_url', data=request_data, timeout=60)
         return r.json()
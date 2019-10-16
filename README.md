# temoto-commander-proxy
Heroku server for capturing Google Assistant and Amazon Alexa queries, which can later be easily accessed from private networks. 

This service should be configured as a webhook/endpoint in Google Actions or Amazon Alexa Skills Kit accordingly.
* For Google Actions, set this as the *webhook*: https://temoto-commander-proxy.herokuapp.com/google-webhook
* For Amazon Alexa Skill, set this as the *endpoint*: https://temoto-commander-proxy.herokuapp.com/alexa-webhook

In order to read the queries:
* For Google Action queries, go to: https://temoto-commander-proxy.herokuapp.com/google-queries
* For Amazon Alexa Skill queries, go to: https://temoto-commander-proxy.herokuapp.com/alexa-queries

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


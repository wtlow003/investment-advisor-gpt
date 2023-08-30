# InvestmentAdvisorGPT

> Your friendly investment advisor has now turned into an LLM chatbot!

This project demonstrates the usage of custom agent with knowledge base and tools to generate insightful conversations with regards to investment-related topics and products.

The chatbot demonstrated in this repo exhibits certain persona [defined](./src/model/templates/tools.py) aimed to conduct a sale outreach with users in attempt to promote and pitch certain financial products e.g., mutual funds embedded within our knowledge base. Conversation flows are also depended on previous conversation history. The attempt to generate context-aware sales conversation is adapted from [SalesGPT](https://github.com/filip-michalsky/SalesGPT), where the chatbot has the ability to shift conversation topics with minimal prompting from the user.

## Installation

The application consisting of the UI and server is container-ready and deployed via the [docker-compose](docker-compose.yaml) file.

To start the application, simply use the following command:

```docker
docker-compose up -build
```

To stop the application and clean up, use the following command:

```docker
docker-compose down --remove-orphans
```

### Tools and LLM Setup

To ensure the full working experience of the chatbot, you will need to have the following API keys:

1. **OpenAI** via @ https://platform.openai.com/
   - This powers the underlying LLM model (`ChatOpenAI`).
2. **Serper** via @ https://serper.dev/
   - This powers the underlying web search capability (`GoogleSerperAPIWrapper`)

Once you have obtained the relevant API keys, you can stored them in a [.env](./.env) file, in the following format:

```
OPENAI_API_KEY="fill me in"
SERPER_API_KEY="fill me in"
```

## Quick Start
Using your terminal:
```bash
# user_id can be anything, it just to use to create
# and identify your agent to retrieve relevant conversation history/context
export user_id="jensenlwt"

# initial message is empty as the bot will chat with you first
curl -X POST http://localhost:8000/chat/$user_id \
     -H "Content-Type: application/json" \
     -d '{"message": ""}'

>>> {
    "user_id":"jensenlwt",
    "raw_message":"Bobby Axelrod: Hi Jensen! How are you doing today? <END_OF_TURN>"
    }

# asking about new opportunities
curl -X POST http://localhost:8000/chat/$user_id \
     -H "Content-Type: application/json" \
     -d '{"message": "I am doing good Bobby! Do you have any new investment opportunities for me?"}'

>>> {"user_id":"jensenlwt",
    "raw_message":"Bobby Axelrod: Hi Jensen! I'm glad to hear that you're doing good. Yes, I do have some exciting new investment opportunities for you. We have recently launched various mutual funds from Abrdn that might be of interest to you. These funds are professionally managed by different fund managers and designed to meet your specific investment needs. Would you like me to provide more information about these funds? <END_OF_TURN>"
}

# seeking new information
curl -X POST http://localhost:8000/chat/$user_id \
     -H "Content-Type: application/json" \
     -d '{"message": "Sure! can you kindly provide me with more information?"}'

>>> {
  "user_id": "jensenlwt",
  "raw_message": "Bobby Axelrod: Absolutely, Jensen! Here are a few mutual funds from Abrdn that you might find interesting:\n\n1. Abrdn Global Technology Fund: This fund focuses on investing in global technology companies, aiming to capitalize on advancements in the tech sector.\n\n2. Abrdn Emerging Markets Equity Fund: This fund targets emerging market economies and invests in high-potential companies within those markets, aiming for long-term capital growth.\n\n3. Abrdn Sustainable Equity Fund: This fund invests in companies that actively contribute to sustainable development and environmental responsibility, aiming to generate both financial returns and positive impact.\n\n4. Abrdn Global Bond Fund: This fund focuses on fixed-income securities from around the world, aiming to provide stable income and potential capital appreciation.\n\nThese are just a few options available, Jensen. Let me know if any of these funds caught your interest, or if you'd like more information on any specific one. <END_OF_TURN>"
}
```

#### UI

![chat ui](docs/chat-ui.png)

In addition to using API calls, a UI is provided. The UI is developed using [Chainlit](https://docs.chainlit.io/overview) that allows for fast iteration when building LLM app interfaces.

To visit the UI, you may access @ http://localhost:8080 after completing the relevant [installation](#installation).

## Architecture

![architecture diagram of InvestmentAdvisorGPT](./doc/../docs/Untitled-2023-08-30-0403.png)

### Conversation Context

### Knowledge Base and Tools


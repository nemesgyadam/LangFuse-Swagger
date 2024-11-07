# LLM-Powered GitHub Code Review Tool 🚀

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Supported-blueviolet?style=flat-square)](https://www.langchain.com/)
[![Langfuse](https://img.shields.io/badge/Langfuse-Integrated-9cf?style=flat-square)](https://www.langfuse.com/)

A powerful, universal FastAPI server that automatically generates endpoints with Swagger UI from any Langfuse project. If you have a Langfuse project with prompts (text or chat) and model configurations, this tool dynamically creates FastAPI endpoints with all required inputs ready to use in Swagger.

## 🌟 Features

- **Dynamic Endpoint Generation**: Creates endpoints automatically from Langfuse project prompts.
- **Supports Chat and Text Templates**: Flexible handling for different prompt types.
- **LangChain Integration**: Connect seamlessly with LangChain  for enhanced language model functionality.
- **Configurable Parameters**: Configure model type, temperature, and other variables directly through Langfuse.
- **Trace Logging**: Records detailed logs of interactions and traces with Langfuse, providing transparency and tracking for each review.

## 🛠️ Setup

1. **API Key Management**:
   - Store your OpenAI API key as an environment variable or set it up directly in `docker-compose`.
   
2. **Langfuse Project Setup**:
   - Create a Langfuse project and configure it to generate prompts.
   - Store Langfuse API keys as environment variables or define them in `docker-compose`.
   
3. **Prompt Configuration**:
   - Define prompts within your Langfuse project; variables from these prompts will automatically appear in Swagger as API inputs.
   - (Optional) Customize prompt configurations by setting parameters like model type and temperature.

4. **API Key Configuration**:
   - The API requires an API key for authentication, passed via the `X-API-Key` header
   - Default API key is set to "42" if not configured
   - Can be customized by setting the `API_KEY` environment variable

5. **Langfuse Tag Filtering**:
   - Filter which prompts are used to generate endpoints using the `LANGFUSE_TAGS` environment variable
   - Specify a comma-separated list of tags (e.g., `LANGFUSE_TAGS="swagger,api,production"`)
   - Prompts with matching tags will be used to create API endpoints, if no tags specified all prompts will be used.

## 🚀 Usage

There are two ways to run the server:

1. **Direct Python Execution**
   ```bash
   python main.py
   ```

2. **Docker Container**
   The application is available as a Docker image: `nemesgyadam/langfuse-swagger`
   
   To launch using docker-compose:
   ```bash
   docker-compose up -d
   ```

### Accessing the API

1. **Swagger Documentation**
   Visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore and interact with the API endpoints through the Swagger UI interface.

2. **Making API Calls**
   Test the endpoints using:
   - Swagger UI's interactive interface
   - HTTP clients like Postman
   - Command line tools like curl

## 🔧 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LANGFUSE_PUBLIC_KEY` | Public key for Langfuse authentication | - | Yes |
| `LANGFUSE_SECRET_KEY` | Secret key for Langfuse authentication | - | Yes |
| `LANGFUSE_HOST` | Langfuse host URL | https://cloud.langfuse.com | No |
| `OPENAI_API_KEY` | OpenAI API key for model access | - | Yes |
| `API_KEY` | API key for endpoint authentication | "42" | No |
| `LANGFUSE_TAGS` | Comma-separated list of tags to filter prompts | - | No |


## 🛠️ Future Enhancements

- [ ] Implement Custom Handlers for additional language model workflows and integrations.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for more details.

## 🤝 Contributing

We welcome contributions, issues, and feature requests! Feel free to explore the [issues page](../../issues) to get involved.

## 📬 Contact

For questions or suggestions, please [open an issue](../../issues/new) or reach out to the maintainers.

Happy Reviewing! 🎉
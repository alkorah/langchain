import json

class SwaggerProcessor:
    def __init__(self, swagger_spec: dict):
        self.spec = swagger_spec

    def extract_information(self):
        endpoints = self.spec.get('paths', {}).keys()
        extracted_info = {}
        for endpoint in endpoints:
            operations = self.spec['paths'][endpoint].keys()
            extracted_info[endpoint] = {}
            for operation in operations:
                parameters = self.spec['paths'][endpoint][operation].get('parameters', [])
                responses = self.spec['paths'][endpoint][operation].get('responses', {})
                response_schemas = {status: resp.get('schema') for status, resp in responses.items() if 'schema' in resp}
                extracted_info[endpoint][operation] = {
                    "parameters": parameters,
                    "response_schemas": response_schemas
                }
        return extracted_info

    def format_for_llm(self, extracted_info):
        formatted_info = []
        for endpoint, operations in extracted_info.items():
            for operation, details in operations.items():
                formatted_info.append(f"Endpoint: {endpoint}\nOperation: {operation}\nParameters: {details['parameters']}\nResponse Schemas: {details['response_schemas']}\n")
        return "\n".join(formatted_info)

# Example usage
if __name__ == "__main__":
    with open('src/swaggerneedfix.json', 'r', encoding='utf-8') as f:
        swagger_spec = json.load(f)
    processor = SwaggerProcessor(swagger_spec)
    extracted_info = processor.extract_information()
    formatted_info = processor.format_for_llm(extracted_info)
    print(formatted_info)

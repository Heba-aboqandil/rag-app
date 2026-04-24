from flask import Flask, render_template, request, jsonify
import boto3
import os
import re

app = Flask(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", "OAVAIYMIV9")
MODEL_ARN = os.getenv("MODEL_ARN", "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0")

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)


def ask_knowledge_base(question: str) -> str:
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN
                }
            }
        )
        raw_text = response["output"]["text"]

        cleaned_text = re.sub(r'Action: .*?(\n|$)', '', raw_text)
        cleaned_text = cleaned_text.replace('Passage:', '').strip()

        return cleaned_text
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Please type a question first."}), 400

    answer = ask_knowledge_base(question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, session
import os
import mysql.connector
from flask_cors import CORS
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.prompts import PromptTemplate
import langchain
from langchain.callbacks import get_openai_callback
from langchain.cache import SQLiteCache
from langchain.embeddings import OpenAIEmbeddings
import asyncio
from dotenv import load_dotenv
import uuid
import httpx

load_dotenv()

# Initialize the Langchain cache
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

# Create a Flask application
app = Flask(__name__, static_folder="static")
CORS(app)

# app.config["DATABASE_HOST"] = "sh021.webhostingservices.com"
# app.config["DATABASE_USER"] = "sngbwjmy_hariprasath"
# app.config["DATABASE_PASSWORD"] = "Neuraza@123"
# app.config["DATABASE_NAME"] = "sngbwjmy_Bluetyga_data"
app.config["TABLE_NAME"] = os.environ.get("chat_logs")
app.config["MAX_TOKENS"] = 100

app.secret_key = "your_secret_key_here"

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host=os.environ.get("DATABASE_HOST"),
    user=os.environ.get("DATABASE_USER"),
    password=os.environ.get("DATABASE_PASSWORD"),
    database=os.environ.get("DATABASE_NAME"),
)

mycursor = mydb.cursor()
executor = ThreadPoolExecutor(max_workers=4)


# Create table if not exists
mycursor.execute(
    f"""
    CREATE TABLE IF NOT EXISTS {app.config['TABLE_NAME']} (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        SessionId VARCHAR(255),
        Question TEXT,
        Prompt_Tokens INT,
        Response TEXT,
        Completion_Tokens INT,
        Total_Tokens DOUBLE,
        Cost DOUBLE,
        Successful_Requests INT,
        UserIP VARCHAR(255),
        UserLocation VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# Initialize the Chatbot
chatbot = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.1,
        model_name="gpt-3.5-turbo",
        max_tokens=200,
    ),
    chain_type="stuff",
    retriever=FAISS.load_local('faiss_bluetyga_docs', OpenAIEmbeddings()).as_retriever(search_type="similarity",
                                                                                       search_kwargs={"k": 1}),
)

# Define the chat template
template = """
Your expertise is in answering queries related to Bluetyga and general conversation only and
act as customer support chatbot. If the question asked is not related to Bluetyga or programming, mathematical, joke and
other irrelevant, please do not answer it. Instead, kindly respond with "I do not have knowledge in
that area I'm sorry, but I'm here to assist you with fashion and Bluetyga."
split the results into subparagraph
{query}?
"""

prompt = PromptTemplate(
    input_variables=["query"],
    template=template,
)


# Function to get user location based on IP address
async def get_user_location(ip):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://ipinfo.io/{ip}/json")
        data = r.json()
        location = f"{data.get('city')}, {data.get('region')}, {data.get('country')}"
        return location


def run_with_callback(message, prompt):
    with get_openai_callback() as cb:
        response = chatbot.run(prompt.format(query=message))
    return response, cb


async def run_chatbot(message):
    loop = asyncio.get_event_loop()
    response, cb = await loop.run_in_executor(executor, run_with_callback, message, prompt)
    return response, cb


# Custom error handler
@app.errorhandler(Exception)
def handle_error(error):
    # Log the error
    app.logger.error(f"An error occurred: {str(error)}")

    # Define error response data
    error_response = {
        "error": "An error occurred",
        "message": str(error),
    }

    return jsonify(error_response), 500


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/predict", methods=["POST"])
async def predict():
    try:
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"answer": "I cannot understand your query!"}), 400

        session_id = session.get("session_id", str(uuid.uuid4()))
        session["session_id"] = session_id

        user_ip = request.remote_addr
        user_location = await get_user_location(user_ip)

        response, cb = await run_chatbot(user_message)

        sql = f"INSERT INTO {app.config['TABLE_NAME']} (SessionId, Question, Prompt_Tokens, " \
              f"Response, Completion_Tokens, Total_Tokens, Cost, Successful_Requests, UserIP, UserLocation) " \
              f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (
            session_id,
            user_message,
            cb.prompt_tokens,
            response,
            cb.completion_tokens,
            cb.total_tokens,
            cb.total_cost,
            cb.successful_requests,
            user_ip,
            user_location,
        )
        mycursor.execute(sql, val)
        mydb.commit()
        return jsonify({"answer": response})

    except Exception as e:
        # Handle other exceptions
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"answer": "An error occurred"}), 500


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80)

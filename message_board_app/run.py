from board import create_app

# refers to __init__.py directly
app = create_app()

# Run the app if this script is executed directly
if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=8000, debug=True)  # Running on port 8000

# alternatively, you can run the app in terminal by python -m flask --app board run --port 8000 --debug
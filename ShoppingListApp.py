import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import speech_recognition as sr
import threading
import pyttsx3

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment

df = pd.read_excel(r'MasterList.xlsx', sheet_name='Sheet1')

items = []
for i in range(len(df)):
    items.append({"name": df["Item"][i], "max": df["Number"][i]})

selections = []

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please say 'yes' or 'no'...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("Could not request results; check your network connection.")
    return None

def ask_question(item):
    question = f"Would you like to select {item['name']}? The maximum quantity is {item['max']}."
    engine.say(question)
    engine.runAndWait()
    print(question)

def voice_input_thread():
    while items:
        if items:
            ask_question(items[0])
        text = get_voice_input()
        if text:
            if 'yes' in text.lower():
                selections.append({"name": items[0]['name'], "quantity": 1})  # Default quantity, can be modified
                items.pop(0)
            elif 'no' in text.lower():
                items.pop(0)

voice_thread = threading.Thread(target=voice_input_thread)
voice_thread.start()

app.layout = dbc.Container([
    html.H2("Shopping List"),
    html.Div(id='item-prompt', style={'fontSize': 20, 'marginBottom': 20}),
    dcc.Dropdown(id='quantity-dropdown', placeholder='Select quantity'),
    html.Br(),
    dbc.Button("Yes", id='yes-button', color='primary', className='me-2'),
    dbc.Button("No", id='no-button', color='secondary'),
    html.Br(), html.Br(),
    html.H4("Selected Items:"),
    html.Div(id='review-output', style={'marginTop': 20, 'whiteSpace': 'pre-wrap'}),
])

@app.callback(
    [Output('item-prompt', 'children'),
     Output('quantity-dropdown', 'options'),
     Output('yes-button', 'disabled'),
     Output('no-button', 'disabled'),
     Output('review-output', 'children')],
    [Input('yes-button', 'n_clicks'),
     Input('no-button', 'n_clicks')],
    [State('quantity-dropdown', 'value')]
)
def update_selection(yes_clicks, no_clicks, quantity):
    ctx = dash.callback_context
    if not ctx.triggered:
        item = items[0] if items else None
        return (
            f"Would you like to select {item['name']}? (Max: {item['max']})" if item else "All items reviewed.",
            [{'label': i, 'value': i} for i in range(1, item['max'] + 1)] if item else [],
            False if item else True,
            False if item else True,
            "\n".join([f"{item['name']}: {item['quantity']}" for item in selections])
        )

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if 'yes-button' in button_id and items:
        if quantity is None:
            return dash.no_update
        selections.append({"name": items[0]['name'], "quantity": quantity})

    if items:
        items.pop(0)

    item = items[0] if items else None
    return (
        f"Would you like to select {item['name']}? (Max: {item['max']})" if item else "All items reviewed.",
        [{'label': i, 'value': i} for i in range(1, item['max'] + 1)] if item else [],
        False if item else True,
        False if item else True,
        "\n".join([f"{item['name']}: {item['quantity']}" for item in selections])
    )

if __name__ == "__main__":
    app.run_server(debug=False)

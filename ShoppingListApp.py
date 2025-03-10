import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment

# Load the Excel file with the specific path
df = pd.read_excel(r'C:\\Users\\Jeremy Levesley\\Documents\\GitHub\\ShoppingList\\MasterList2.xlsx', sheet_name='Sheet1')

# Original items list
original_items = [{"name": df["Item"][i], "max": df["Number"][i]} for i in range(len(df))]
items = original_items.copy()  # Create a mutable copy of the items list
selections = []  # List to store selected items

# Layout
app.layout = dbc.Container([
    html.H2("Dottie's Shopping List"),  # Title changed
    html.Div(id='item-prompt', style={'fontSize': 20, 'marginBottom': 20}),  # Display current item here
    dcc.Dropdown(id='quantity-dropdown', placeholder='Select quantity'),
    html.Br(),
    dbc.Button("Add to List", id='add-button', color='primary', className='me-2'),
    dbc.Button("Skip", id='no-button', color='secondary', className='me-2'),
    dbc.Button("Reset", id='reset-button', color='danger'),
    html.Br(), html.Br(),
    html.H4("Selected Items:"),
    html.Div(id='review-output', style={'marginTop': 20, 'whiteSpace': 'pre-wrap'}),
    
    # Send email button
    dbc.Button("Send Email", id="send-email", color="success", className="me-2"),
    html.Div(id='email-status', style={'marginTop': 20}),
    
    # Centered image of Dottie (Make sure 'dorothy.png' is in the 'assets' folder)
    html.Div([
        html.Img(src='/assets/dorothy.png', style={'width': '200px', 'height': 'auto', 'margin': '0 auto', 'display': 'block'}),
    ], style={'textAlign': 'center', 'marginTop': '30px'})
], fluid=True)

# 📧 Email Sending Function
def send_email(shopping_list):
    from dotenv import load_dotenv
    load_dotenv("C:\\Users\Jeremy Levesley\\ShoppingList\\env_var.env")
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = "jemlevesley11@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")
    print(sender_email)
    print(password)

    # Email Setup
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Your Shopping List"

    # Email Body
    body = "Here is your shopping list:\n\n" + "\n".join([f"{item['name']}: {item['quantity']}" for item in shopping_list])
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail's SMTP server (change for other providers)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return "✅ Email Sent Successfully!"
    except Exception as e:
        return f"❌ Email Sending Failed: {str(e)}"

# Callback for managing items
@app.callback(
    [Output('item-prompt', 'children'),  # Displays the item being reviewed
     Output('quantity-dropdown', 'options'),  # Updates the dropdown options
     Output('add-button', 'disabled'),  # Disables add button when there are no items
     Output('no-button', 'disabled'),  # Disables skip button when there are no items
     Output('review-output', 'children')],  # Displays selected items
    [Input('add-button', 'n_clicks'),
     Input('no-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('quantity-dropdown', 'value')]
)
def update_list(add_clicks, no_clicks, reset_clicks, quantity):
    global items, selections
    ctx = dash.callback_context

    # Detect which button was clicked
    if not ctx.triggered:
        item = items[0] if items else None
        return (
            f"Item: {item['name']} (Max: {item['max']})" if item else "All items reviewed.",
            [{'label': i, 'value': i} for i in range(1, item['max'] + 1)] if item else [],
            False if item else True,
            False if item else True,
            generate_selected_items(selections)
        )

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'reset-button':
        # Reset the list and selections
        items.clear()
        items.extend(original_items)  # Restore the original list
        selections.clear()
        item = items[0] if items else None
        return (
            f"Item: {item['name']} (Max: {item['max']})" if item else "All items reviewed.",
            [{'label': i, 'value': i} for i in range(1, item['max'] + 1)] if item else [],
            False if item else True,
            False if item else True,
            generate_selected_items(selections)
        )

    if button_id == 'add-button' and items:
        if quantity is None:
            return dash.no_update
        selections.append({"name": items[0]['name'], "quantity": quantity})  # Add item to selected list
        items.append(items.pop(0))  # Move current item to the end of the list

    elif button_id == 'no-button' and items:
        items.append(items.pop(0))  # Skip the current item and rotate it to the end of the list

    item = items[0] if items else None
    return (
        f"Item: {item['name']} (Max: {item['max']})" if item else "All items reviewed.",
        [{'label': i, 'value': i} for i in range(1, item['max'] + 1)] if item else [],
        False if item else True,
        False if item else True,
        generate_selected_items(selections)
    )

def generate_selected_items(selections):
    """Generate the selected items list."""
    return html.Ul([html.Li([f"{item['name']}: {item['quantity']} "]) for item in selections])

# Callback for sending the email
@app.callback(
    Output('email-status', 'children'),
    Input('send-email', 'n_clicks'),
    prevent_initial_call=True
)
def send_shopping_list(n_clicks):
    if selections:
        return send_email(selections)  # Send the selected items as the shopping list
    return "❌ No items selected to send."

if __name__ == "__main__":
    app.run_server(debug=False)  # Run the app

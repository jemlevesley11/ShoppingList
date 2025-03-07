import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Needed for deployment

df = pd.read_excel(r'MasterList2.xlsx', sheet_name='Sheet1')

items = []
for i in range(len(df)):
    items.append({"name": df["Item"][i], "max": df["Number"][i]})

selections = []

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

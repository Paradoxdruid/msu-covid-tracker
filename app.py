import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.title = "MSU COVID"


# Functions
def make_graph(csv_filename):
    """Take in a dataframe and make a pretty interactive graph.

    Args:
        csv_filename (str): csv_filename

    Returns:
        fig: plotly figure object
    """

    df = pd.read_csv(csv_filename, header=0)
    df["Date"] = pd.to_datetime(df["Date"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Case"],
            mode="lines+markers+text",
            name="Total Cases",
            text=df["Case"],
            textposition="top center",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["New"],
            mode="lines+markers+text",
            name="New Cases",
            text=df["New"],
            textposition="top center",
        )
    )
    fig.update_layout(
        # title="COVID Cases at MSU Denver",
        xaxis_title="Date",
        yaxis_title="Cases",
        template="ggplot2",
        # color_discrete_sequence=colors.sequential.Rainbow_r,
        #     height=500,
        #     width=900,
        legend=dict(orientation="v", yanchor="bottom", y=0.4, xanchor="right", x=1),
    )

    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")

    fig.update_xaxes(dtick="D1", tickformat="%b %d")

    return fig


app.layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    # dbc.CardImg(src=app.get_asset_url("msu_covid.png"), top=True),
                    dbc.CardHeader(
                        html.H4("MSU Denver COVID Cases", className="card-title"),
                    ),
                    dbc.CardBody([dcc.Graph(figure=make_graph("msu_covid.csv"))]),
                ],
                # style={"width": "18rem"},
            ),
            width={"size": 6, "offset": 3},
        ),
        style={"padding-top": "40px"},
    ),
    fluid=True,
)

if __name__ == "__main__":
    app.run_server()

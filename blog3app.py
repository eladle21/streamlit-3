import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
file_path = 'player_avg_df.csv'
data = pd.read_csv(file_path)

if 'PLAYER_ID' in data.columns:
    data = data.drop(columns=['PLAYER_ID'])

# App title and description
st.title("Basketball Player Performance Dashboard")
st.markdown("""
Explore detailed basketball player statistics, filter data, and uncover insights interactively. Use the tools provided to filter, visualize, and understand the data.
""")

# Sidebar for filtering
st.sidebar.header("Filters")
teams = st.sidebar.multiselect("Select Teams", data['TEAM_ABBREVIATION'].unique(),
                               default=data['TEAM_ABBREVIATION'].unique())
min_games = st.sidebar.slider("Minimum Games Played", 0, int(data['GP'].max()), 0)

filtered_data = data[(data['TEAM_ABBREVIATION'].isin(teams)) & (data['GP'] >= min_games)]

# Tab structure for different analyses
tab1, tab2, tab3 = st.tabs(["Summary", "Visual Analysis", "Player Comparison"])

# Tab 1: Summary statistics
with tab1:
    st.header("Summary Statistics")
    st.write("Basic statistics for the filtered dataset:")
    st.write(filtered_data.describe())

# Tab 2: Visual Analysis
with tab2:
    st.header("Visual Analysis")
    st.markdown("Explore trends and patterns in player performance:")

    # Dropdown for metric selection
    metric = st.selectbox("Choose a metric to visualize", ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PLUS_MINUS'])

    # Create a Plotly bar chart
    team_avg = filtered_data.groupby('TEAM_ABBREVIATION')[metric].mean().reset_index()
    fig = px.bar(team_avg, x='TEAM_ABBREVIATION', y=metric,
                 title=f"Average {metric} by Team",
                 labels={'TEAM_ABBREVIATION': 'Team', metric: f'Average {metric}'},
                 color='TEAM_ABBREVIATION',
                 template='plotly_dark')
    st.plotly_chart(fig)

# Tab 3: Player Comparison
with tab3:
    st.header("Player Comparison")
    st.markdown("Compare two players side by side:")

    player1 = st.selectbox("Select Player 1", filtered_data['PLAYER_NAME'].unique(), key="player1")
    player2 = st.selectbox("Select Player 2", filtered_data['PLAYER_NAME'].unique(), key="player2")

    p1_stats = filtered_data[filtered_data['PLAYER_NAME'] == player1]
    p2_stats = filtered_data[filtered_data['PLAYER_NAME'] == player2]

    # Radar chart for comparison with raw counts in tooltip and cleaner visuals
    metrics = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']

    # Normalize stats for player comparison (for scaling purposes)
    normalized_data = pd.DataFrame({
        "Metric": metrics,
        player1: [(p1_stats.iloc[0][metric] - filtered_data[metric].min()) /
                  (filtered_data[metric].max() - filtered_data[metric].min()) for metric in metrics],
        player2: [(p2_stats.iloc[0][metric] - filtered_data[metric].min()) /
                  (filtered_data[metric].max() - filtered_data[metric].min()) for metric in metrics],
        f"{player1}_raw": [p1_stats.iloc[0][metric] for metric in metrics],
        f"{player2}_raw": [p2_stats.iloc[0][metric] for metric in metrics]
    })

    # Convert 'Metric' column to a list for use in theta
    theta_values = normalized_data["Metric"].tolist()

    # Create radar chart traces
    fig = px.line_polar(
        normalized_data,
        r=normalized_data[player1],
        theta=theta_values,
        line_close=True,
        template="plotly_dark",
        hover_data={f"{player1}_raw": True, f"{player2}_raw": False}
    )
    fig.add_scatterpolar(
        r=normalized_data[player2],
        theta=theta_values,
        mode="lines",
        fill='toself',
        name=player2,
        hovertemplate='<b>%{theta}</b><br>Value: %{customdata}<extra></extra>',
        customdata=normalized_data[f"{player2}_raw"]
    )

    # Update layout
    fig.data[0].name = player1
    fig.data[0].hovertemplate = '<b>%{theta}</b><br>Value: %{customdata}<extra></extra>'
    fig.data[0].customdata = normalized_data[f"{player1}_raw"]
    fig.data[1].name = player2
    fig.update_layout(
        title="Player Performance Comparison",
        showlegend=True,
        polar=dict(
            radialaxis=dict(visible=False)  # Hide axis values
        )
    )

    st.plotly_chart(fig)

# Expander for dataset preview
with st.expander("Dataset Preview"):
    st.dataframe(filtered_data)
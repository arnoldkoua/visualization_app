import streamlit as st
import pandas as pd
import plotly.express as px
from openpyxl import load_workbook, Workbook

# Set page title
st.set_page_config(page_title="Data Visualization App", page_icon=":bar_chart:")
# Set sidebar width
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        width: 500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Data Visualization App")
st.write("Upload your Excel files below. This application makes it possible to visualize data.")

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data into a Pandas dataframe
    # data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        try:
            data = pd.read_excel(uploaded_file)
        except:
            data = pd.read_excel(uploaded_file, engine='openpyxl')

    # Display the loaded data
    st.write("## Data")
    st.write(data.head())

    # Create sidebar to select variable types
    st.sidebar.header("Select Variable Type")
    var_type = st.sidebar.selectbox("", ["Numerical", "Categorical"])

    # Create sidebar to select variables
    if var_type == "Numerical":
        st.sidebar.header("Select Numerical Variables")
        numerical_cols = list(data.select_dtypes(include=['float64', 'int64']).columns)
        selected_cols = st.sidebar.multiselect("", numerical_cols)

    elif var_type == "Categorical":
        st.sidebar.header("Select Categorical Variables")
        categorical_cols = list(data.select_dtypes(include=['object']).columns)
        selected_cols = st.sidebar.multiselect("", categorical_cols)

    # Visualize numerical variables
    if var_type == "Numerical":
        st.header("Numerical Variables")

        if selected_cols:
            numerical_data = data[selected_cols]
            st.write(numerical_data.describe())

            # Create histogram for each variable
            for col in selected_cols:
                st.write(f"### {col}")

                # Allow user to name the graph
                graph_name = st.text_input("Name your graph", value=f"{col} histogram")

                # Create slider for number of bins
                bins = st.slider(f"Select number of bins for {col}", min_value=5, max_value=50, value=20)

                # Create histogram using Plotly
                fig = px.histogram(numerical_data, x=col, nbins=bins, title=graph_name)
                fig.update_layout(xaxis_title=col, yaxis_title="Count")
                fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
                st.plotly_chart(fig)

    # Visualize categorical variables
    elif var_type == "Categorical":
        st.header("Categorical Variables")

        if selected_cols:
            categorical_data = data[selected_cols]
            st.write(categorical_data.describe())

            # Create count plot for each variable
            for col in selected_cols:
                st.write(f"### {col}")

                # Allow user to name the graph
                graph_name = st.text_input("Name your graph", value=f"{col} count plot")

                # Create count plot using Plotly
                fig = px.histogram(categorical_data, x=col, title=graph_name)
                fig.update_layout(xaxis_title=col, yaxis_title="Count")
                fig.update_xaxes(type='category')
                fig.update_traces(texttemplate='%{y}', textposition='inside')
                fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
                st.plotly_chart(fig)

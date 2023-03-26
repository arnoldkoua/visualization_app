import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import base64
import io
from xlsxwriter import Workbook
from openpyxl import load_workbook, Workbook

def get_session_state():
    """Create a dictionary for storing session state"""
    return st.session_state

session_state = get_session_state()

def page_upload():
    st.title("Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            try:
                data = pd.read_excel(uploaded_file)
            except:
                data = pd.read_excel(uploaded_file, engine='openpyxl')

        # Save the data in the session state
        session_state.data = data

        st.success("Data uploaded successfully.")

def page_visualize():
    st.title("Visualize Data")

    if "data" not in st.session_state:
        st.warning("Please upload a data file first.")
        return

    data = st.session_state.data

    st.write("## Data")
    st.write(data.head())

    st.sidebar.header("Select Variables")

    numerical_cols = list(data.select_dtypes(include=['float64', 'int64']).columns)
    categorical_cols = list(data.select_dtypes(include=['object']).columns)

    selected_numerical_cols = st.sidebar.multiselect("Numerical Variables", numerical_cols)
    selected_categorical_cols = st.sidebar.multiselect("Categorical Variables", categorical_cols)

    if selected_numerical_cols:
        st.header("Numerical Variables")

        numerical_data = data[selected_numerical_cols]
        st.write(numerical_data.describe())

        for col in selected_numerical_cols:
            st.write(f"### {col}")

            bins = st.slider(f"Select number of bins for {col}", min_value=5, max_value=50, value=20)

            graph_name = st.text_input("Name your graph", value=f"{col} histogram")
            xaxis_name = st.text_input("Name your x axis", value=f"{col}")

            fig = px.histogram(numerical_data, x=col, nbins=bins, title=graph_name)
            fig.update_layout(xaxis_title=xaxis_name, yaxis_title="Freq.")
            fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
            st.plotly_chart(fig)

    if selected_categorical_cols:
        st.header("Categorical Variables")

        categorical_data = data[selected_categorical_cols]
        st.write(categorical_data.describe())

        for col in selected_categorical_cols:
            st.write(f"### {col}")

            graph_name = st.text_input("Name your graph", value=f"{col} count plot")

            fig = px.histogram(categorical_data, x=col, title=graph_name)
            fig.update_layout(xaxis_title=None, yaxis_title="Freq.", yaxis_visible=False)
            fig.update_xaxes(type='category')
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
            st.plotly_chart(fig)

def to_excel(df):
    """Converts a pandas DataFrame to an Excel file."""
    excel_file = io.BytesIO()
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(writer, index=True)
    writer.save()
    excel_file.seek(0)
    return excel_file.getvalue()

def download_button(data, filename, fileformat):
    """Creates a download button for a file."""
    if fileformat == 'csv':
        filedata = to_csv(data)
        mime_type = 'text/csv'
        file_ext = 'csv'
    elif fileformat == 'excel':
        filedata = to_excel(data)
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_ext = 'xlsx'
    else:
        raise ValueError(f"Unsupported file format: {fileformat}")
    b64 = base64.b64encode(filedata).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}.{file_ext}">Download {filename} ({file_ext})</a>'
    return href

def page_cross_tables():
    st.title("Cross Tables")

    if "data" not in st.session_state:
        st.warning("Please upload a data file first.")
        return

    data = st.session_state.data

    st.write("### Data")
    st.write(data.head())

    st.sidebar.header("Select Variables")

    categorical_cols = list(data.select_dtypes(include=['object']).columns)
    numeric_cols = list(data.select_dtypes(include=['float', 'int']).columns)

    selected_categorical_cols = st.sidebar.multiselect("Categorical Variables", categorical_cols)

    if selected_categorical_cols:
        # Generate cross tables and plots for all pairs of selected categorical variables
        for i in range(len(selected_categorical_cols)):
            for j in range(i+1, len(selected_categorical_cols)):
                x_col = selected_categorical_cols[i]
                y_col = selected_categorical_cols[j]
                ct = pd.crosstab(data[x_col], data[y_col], normalize='index')

                # Display cross table
                # st.write(f"## Cross Table: {x_col} vs {y_col}")
                # st.write(ct)
                st.markdown(download_button(ct, f"{x_col}_vs_{y_col}_cross_table", 'excel'), unsafe_allow_html=True)

                # Create and display Plotly graph
                graph_name = st.text_input("Name your graph :", value=f"{x_col}_vs_{y_col}_cross_table")
                # xaxis_name = st.text_input("Name your x axis :", value=f"{x_col}")

                fig = px.bar(ct, barmode='group', labels={'index': x_col, 'value': 'Proportion'})
                fig.update_layout(
                title=graph_name,
                legend_title=None,
                xaxis_title=None,
                yaxis_title=None,
                yaxis_visible=False
                )
                fig.update_traces(texttemplate='%{y:.1%}', textposition='outside')
                fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
                st.plotly_chart(fig)

    else:
        st.warning("Please select at least one categorical variable.")

def page_average_by_categorical():
    st.title("Mean Tables")

    if "data" not in st.session_state:
        st.warning("Please upload a data file first.")
        return

    data = st.session_state.data

    st.write("### Data")
    st.write(data.head())

    st.sidebar.header("Select Variables")

    numerical_cols = list(data.select_dtypes(include=['float64', 'int64']).columns)
    categorical_cols = list(data.select_dtypes(include=['object']).columns)

    selected_numerical_cols = st.sidebar.multiselect("Numerical Variables", numerical_cols)
    selected_categorical_cols = st.sidebar.multiselect("Categorical Variables", categorical_cols)

    if selected_numerical_cols and selected_categorical_cols:
        # st.header("Mean by Categorical Variables")

        for cat_col in selected_categorical_cols:
            st.write(f"### {cat_col}")

            avg_data = round(data[selected_numerical_cols + [cat_col]].groupby(cat_col).mean(), 0)
            st.write(avg_data)
            st.markdown(download_button(avg_data, f"{cat_col}_mean_table", 'excel'), unsafe_allow_html=True)
    else:
        st.warning("Please select at least one categorical and mumeric variables.")

def page_cross_table_with_pivot_table():
    st.title("Cross Table with Pivot Table")

    if "data" not in st.session_state:
        st.warning("Please upload a data file first.")
        return

    data = st.session_state.data

    st.write("### Data")
    st.write(data.head())

    st.sidebar.header("Select Variables")

    numerical_cols = list(data.select_dtypes(include=['float64', 'int64']).columns)
    categorical_cols = list(data.select_dtypes(include=['object']).columns)

    selected_categorical_cols = st.sidebar.multiselect("Select variables to cross:", categorical_cols)
    selected_numerical_cols = st.sidebar.selectbox("Select a numeric variable:", numerical_cols)

    if selected_numerical_cols and selected_categorical_cols:
        # st.header("Mean by Categorical Variables")
        cross_data =  data.pivot_table(values=[selected_numerical_cols], index=selected_categorical_cols, aggfunc=np.mean)
        st.write(cross_data)
        st.markdown(download_button(cross_data, f"{selected_numerical_cols}_cross_table", 'excel'), unsafe_allow_html=True)

        #for cat_col in selected_categorical_cols:
            #st.write(f"### {cat_col}")

            #avg_data = round(data[selected_numerical_cols + [cat_col]].groupby(cat_col).mean(), 0)
            #st.write(avg_data)
            #st.markdown(download_button(avg_data, f"{cat_col}_mean_table", 'excel'), unsafe_allow_html=True)
    else:
        st.warning("Please select at least one categorical and mumeric variables.")

# Define the pages
PAGES = {
    "Upload Data": page_upload,
    "Visualize Data": page_visualize,
    "Cross Tables": page_cross_tables,
    "Means Tables": page_average_by_categorical,
    "Cross With Pivot Tables": page_cross_table_with_pivot_table
}

def main():
    st.set_page_config(page_title="Data Visualization App", page_icon=":bar_chart:")
    st.sidebar.title("Navigation Menu")
    page = st.sidebar.radio("", list(PAGES.keys()))

    # Display the selected page with the session state
    PAGES[page]()

if __name__ == "__main__":
    main()

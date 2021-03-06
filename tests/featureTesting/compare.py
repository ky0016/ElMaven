"""
This module compares different output of cli

List of functions:

1. compare: Compare all the outputs generated from multiple
    cli instances

2. load_files: Loads every file present in the input list into a
    pandas dataframe

3. remove_outliers: Remove rows whose mzs and rts are not equal

4. remove_outliers_using_diff: Remove outliers in pandas dataframe
    on the basis of mzs and rts difference

5. remove_outliers_using_score: Remove outliers in pandas dataframe
    on the basis of score and duplicates

6. plot: scatter plot for comparing single sample from two pandas
    dataframes

7. get_layout: Returns layout for plotly

"""
import os

import plotly.graph_objs as go
from plotly.offline import plot

from helper import helper
from config import config


class CompareOutput(object):
    """
    This class compares different outputs of Cli generated using
    different configuration files
    """

    def __init__(self, file_list, config_name):
        self.file_list = file_list
        self.config_name = config_name
        self.config = config.Config()
        helper.make_dir(self.config.result_dir)

    def compare(self):
        """
        Compare all the outputs generated from multiple
        cli instances
        """

        df_list = self.load_files(self.file_list)
        merged_df = helper.merge_dfs(df_list, self.config.unique_identifiers)
        merged_df = self.remove_outliers(merged_df)
        self.plot(merged_df, self.config.sample_list)

    def load_files(self, file_list):
        """
        Loads every file present in the input list into a pandas
        dataframe
        Args:
            file_list (list): List of paths of files
        Returns:
            df_list (list): List of pandas dataframes
        """
        df_list = []

        for fpath in file_list:
            pdataframe = helper.load_df(fpath)
            df_list.append(pdataframe)

        return df_list

    def remove_outliers(self, pandas_df):
        """
        Remove rows whose mzs and rts are not equal
        Args:
            pandas_df (df): Merged pandas dataframe
        Returns:
            pandas_df (df): Pandas dataframe after outliers
                are removed
        """

        pandas_df = self.remove_outliers_using_diff(pandas_df)
        pandas_df = pandas_df.sort_values("score")
        pandas_df = self.remove_outliers_using_score(pandas_df)

        return pandas_df

    def remove_outliers_using_diff(self, pandas_df):
        """
        Remove outliers in pandas dataframe on the basis
        of mzs and rts difference
        Args:
            pandas_df (df): Pandas dataframe
        Returns:
            pandas_df (df): Pandas dataframe
        """

        for index, row in pandas_df.iterrows():

            mz_1 = row["medMz_x"]
            mz_2 = row["medMz_y"]
            rt_1 = row["medRt_x"]
            rt_2 = row["medRt_y"]

            mz_diff = abs(mz_2 - mz_1)
            rt_diff = abs(rt_2 - rt_1)

            pandas_df["score"] = mz_diff + rt_diff

            if mz_diff < 0.3 and rt_diff < 0.2:
                pass
            else:
                pandas_df.drop(index, inplace=True)

        return pandas_df

    def remove_outliers_using_score(self, pandas_df):
        """
        Remove outliers in pandas dataframe on the basis
        of score and duplicates
        Args:
            pandas_df (df): Pandas dataframe
        Returns:
            pandas_df (df): Pandas dataframe
        """

        mzrt1 = []
        mzrt2 = []

        for index, row in pandas_df.iterrows():

            mz_1 = row["medMz_x"]
            mz_2 = row["medMz_y"]
            rt_1 = row["medRt_x"]
            rt_2 = row["medRt_y"]

            key_1 = (mz_1, rt_1)
            key_2 = (mz_2, rt_2)

            if key_1 in mzrt1 or key_2 in mzrt2:
                pandas_df.drop(index, inplace=True)
            else:
                mzrt1.append(key_1)
                mzrt2.append(key_2)

        return pandas_df

    def plot(self, pandas_df, sample_list):
        """
        Plot scatter plot for comparison single sample from two pandas
        dataframes

        Args:
            pandas_df (df): Merged pandas dataframe
        """

        data = []

        for sample_name in sample_list:
            sample_name_x = sample_name + '_x'
            sample_name_y = sample_name + '_y'
            x = []
            y = []

            for index, row in pandas_df.iterrows():
                x.append(row[sample_name_x])
                y.append(row[sample_name_y])

            trace = go.Scatter(
                x=x,
                y=y,
                name=sample_name,
                mode='markers'
            )

            data.append(trace)

        layout = self.get_layout(
            self.config_name, self.file_list[0], self.file_list[1])

        fig = go.Figure(data=data, layout=layout)

        plot(fig, filename=os.path.join(
            self.config.result_dir, self.config_name + self.config.plot_result))

    def get_layout(self, plot_title, x_title, y_title):
        """
        Returns layout for plotly

        Args:
            plot_title (str): Title of plot
            x_title (str): Title of x axis
            y_title (str): Title of y axis
        Returns:
            layout (plotly obj): Layout for plotly
        """

        layout = go.Layout(
            title=plot_title,
            xaxis=dict(
                title=x_title,
                type='log'
            ),
            yaxis=dict(
                title=y_title,
                type='log'
            )
        )

        return layout

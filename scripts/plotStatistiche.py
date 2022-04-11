import pandas as pd
from math import pi
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models.tools import BoxZoomTool, ResetTool
from bokeh.models import DatetimeTickFormatter
from bokeh.layouts import column
import os
import json
from bokeh.embed import json_item


PATH_TO_DATA = './issues.csv'
PATH_TO_PLOT = './plot/'


def load_issue_data():
    issues = pd.read_csv(PATH_TO_DATA,
            parse_dates=['updated_at', 'created_at'],
            index_col='id')

    s = issues['labels'].apply(eval).explode()
    p = pd.crosstab(s.index, s)
    labels = p.columns.to_list()
    for l in ['tweet', 'telegram-channel', 'Valid/Accettato', 'Services', 'AA Violation']:
        if l in labels:
            labels.remove(l)

    issues = issues.join(p)
    return issues, labels

def issues_by_category_plot(issues: pd.DataFrame, labels: list):
    labels_count = [issues[l].sum() for l in labels]
    sorted_labels = sorted(labels, key=lambda x: labels_count[labels.index(x)])

    p = figure(y_range=sorted_labels,
                title='Number of issues per category',
                x_axis_label="Number of issues",
                y_axis_label="Categories",
                tools='save,hover',
                tooltips="@labels: @count"
    )
    p.toolbar.logo = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    source = dict(labels=labels, count=labels_count)
    p.hbar(y='labels', right='count', height=0.9, source=source)
    return p

def cumulative_sum_issue_over_time(issues):
    data = issues.groupby(issues['created_at'].dt.date)['url'].count().cumsum()
    data.index = pd.to_datetime(data.index)
    data = data.resample('D').ffill()
    p = figure(width=800, height=250,
                title="Issues cumulative sum",
                x_axis_label='Date',
                y_axis_label='Cumulative sum',
                x_axis_type="datetime",
                tools='save')
    p.toolbar.logo = None
    p.line(data.index, data.values, line_width=2)
    p.xaxis.major_label_orientation = pi/4
    p.xaxis[0].formatter = DatetimeTickFormatter(days="%d/%m/%y")
    p.xaxis[0].ticker.desired_num_ticks = 10
    return p

def issues_by_region(labels):
    issues_by_region = issues.groupby('regione')['url'].count()
    issues_by_region = issues_by_region.sort_values()
    
    p = figure(y_range=issues_by_region.index.to_list(),
                title='Number of issues per Italian region',
                x_axis_label="Number of issues",
                y_axis_label="Regions",
                tools='save,hover',
                tooltips="@regioni: @count"
    )
    p.toolbar.logo = None
    p.ygrid.grid_line_color = None
    p.x_range.start = 0
    source = dict(regioni=issues_by_region.index.to_list(), count=issues_by_region.values)
    p.hbar(y='regioni', right='count', height=0.9, source=source)
    return p

if __name__ == '__main__':
    issues, labels = load_issue_data()
    plot1 = cumulative_sum_issue_over_time(issues)
    plot2 = issues_by_category_plot(issues, labels)
    plot3 = issues_by_region(labels)
    
    grid = column(plot1, plot2, plot3)
    # show(grid) # open plot in browser

    with open(os.path.join(PATH_TO_PLOT, 'plot.json'), 'w') as f:
        json.dump(json_item(grid, "statplot"), f)


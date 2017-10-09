@app.route('/grid/<groupname>/')
def grid(groupname):
    # read in the csv file and convert it to a Pandas data frame
    data = pd.DataFrame(pd.read_csv('static/data/chunks/' + groupname + '.csv'))
    # construct a plot of two variables
    data.time = pd.to_datetime(data['CUST_OPN_DT'], format='%m/%d/%Y')
    data.set_index(['CUST_OPN_DT'])
    # select only numeric columns
    floats = data.select_dtypes(include=['float64'])
    # plot the distribution for each float
    for i in range(len(floats.columns)):
        somethin.append(plot_distribution(data, i))
    print(somethin)
    # return your template and objects
    return render_template("intro.html", name=groupname)


# a crude and hastily put together function to plot distributions. don't judge me.
def plot_distribution(dataset, variablename):
    try:
        var = dataset[[variablename]].values
        plt.xlim([min(var) - 5, max(var) + 5])
        plot = plt.hist(var)
        plt.savefig('test' + str(variablename) + '.png')
        plt.clf() # clears the figure
        return plot
    except: # too broad of an exception statement
        print('some error, probably variable formatting')
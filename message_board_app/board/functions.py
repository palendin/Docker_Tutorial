import numpy as np

def LinearRegression(x, m, b):
    fx = m*x + b
    return fx

def ExponentialRegression(x, a, b):
    fx = a*np.exp(b*x)
    return fx

def ExponentialRegression2(x, a, b, c):
    fx = a - b*np.exp(-c*x)
    return fx

# add polynomial function
def PolynomialRegression(xdata,ydata,degree):
    coef = np.round(np.polyfit(xdata,ydata,degree),2)
    yfit = np.polyval(coef, xdata)

    return coef, yfit


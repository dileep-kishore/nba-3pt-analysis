#!/usr/bin/env R

library(ggplot2)
require(reshape)
library(TTR)
library(forecast)
library(randomForest)

threep_per <- read.csv('../../results/team_data/comb_3pper.csv')
threep_attempt <- read.csv('../../results/team_data/comb_3pattempt.csv')

threep_anal <- function(fname)
{
    data <- read.csv(fname)
    df <- melt(data, id.vars='X', variable_name = 'teams')
    ggplot(df, aes(X,value)) + geom_line(aes(colour = teams))
    # Smoothing moving average
    col_names <- names(data)
    #FIXME: Fudging data for these two years (Interpolation)
    data[24, 'CHA'] <- 0.353
    data[25, 'CHA'] <- 0.357
    smooth_data <- data.frame(time = data["X"])
    for (col_name in col_names[2:ncol(data)])
    {
        smooth_data[col_name] <- SMA(data[col_name], n=3)
    }
    df2 <- melt(smooth_data, id.vars='X', variable_name = 'teams')

}

threep_per_smooth <- threep_anal('../../results/team_data/comb_3pper.csv')
threep_attempt_smooth <- threep_anal('../../results/team_data/comb_3pattempt.csv')
ggplot(threep_per_smooth, aes(X,value)) + geom_line(aes(colour = teams))

# Trend analysis
#Decomposition
gsw_per <- threep_per$GSW # Did not work
gsw_ts <- ts(gsw_per, start=c(1980))
plot.ts(gsw_ts)
# HoltWinter (exponential smoothing)
gsw_forecasts <- HoltWinters(gsw_ts, beta = NULL, gamma = NULL)
plot(gsw_forecasts)
gsw_forecasts$SSE
gsw_forecasts2 <- forecast.HoltWinters(gsw_forecasts, h=3)
plot.forecast(gsw_forecasts2)
# Auto-correlations
acf(gsw_per)
pacf(gsw_per)
# There is correlation with lag=1
#Arima
plot(gsw_per, lag(gsw_per))
model1 <- arima(gsw_per, order=c(1,0,0))
model1$aic
# Auto arima model
auto.arima(gsw_per) # wasn't first choice because didn't have enough data points
# arima(0,1,0) is a random walk

#Linear model fitting

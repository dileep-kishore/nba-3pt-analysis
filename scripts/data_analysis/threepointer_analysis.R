#!/usr/bin/env R

library(ggplot2)
require(reshape)
library(TTR)

data <- read.csv('../../results/team_data/final_dataframe.csv')
df <- melt(data, id.vars='X', variable_name = 'teams')
ggplot(df, aes(X,value)) + geom_line(aes(colour = teams))

# Smoothing moving average
col_names <- names(data)
data[24, 'CHA'] <- 0.353
data[25, 'CHA'] <- 0.357
smooth_data <- data.frame(time = data["X"])
for (col_name in col_names[2:ncol(data)])
{
    smooth_data[col_name] <- SMA(data[col_name], n=3)
}
df2 <- melt(smooth_data, id.vars='X', variable_name = 'teams')
ggplot(df2, aes(X,value)) + geom_line(aes(colour = teams))

#Linear model fitting

#Arima

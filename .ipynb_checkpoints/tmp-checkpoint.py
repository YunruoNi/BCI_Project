df2 = df[(df['Spatial Step']==3) & (df['Event']=='SR') & (df['Time Start']==0.6) & (df['Time Span']==0.2)]
# plot_heatmap_df(df2, vmin=0.5)
ac0 = df2[df2['Motor_Status']==0]['Accuracy']
ac1 = df2[df2['Motor_Status']==1]['Accuracy']
gauss = True
for eone in [ac0, ac1]:
    p = shapiro(eone)[1]
    if p < 0.05:
        gauss = False
        break
s1, s2 = ac0, ac1
if gauss:
    p2 = ttest_ind(s1,s2, alternative='greater')[1]
else:
    p2 = mannwhitneyu(s1,s2, alternative='greater')[1]
p2
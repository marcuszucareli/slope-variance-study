import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from database import database


# Draw the slope
def get_slope_fig(height, ratio):
    
	# Define the distance between the border and the beggining and ending of the slope
	dist_to_slope = 5
	
	# Define the max size of all the figures (considering the biggest slope will be 1:3, 15m)
	x_max = 2 * dist_to_slope + 3 * 15

	# Define top and bottom coordinates of the slope
	x_top = x_max / 2 - height * ratio / 2
	y_top = x_max / 2 + height / 2
	x_bottom = x_max / 2 + height * ratio / 2   
	y_bottom = x_max / 2 - height / 2

	# Defining the points for slope and aky poligon
	p1 = (0, y_top)
	p2 = (x_top, y_top)
	p3 = (x_bottom, y_bottom)
	p4 = (x_max, y_bottom)
	p5 = (x_max, 0)
	p6 = (0, 0)
	p7 = (0, x_max)
	p8 = (x_max, x_max)

	slope_points = [p1, p2, p3, p4, p5, p6]
	sky_points = [p1, p2, p3, p4, p8, p7]

	x_slope = []
	y_slope = []
	x_sky = []
	y_sky = []

	for i, slope in enumerate(slope_points):
		current_slope = slope_points[i]
		sky = sky_points[i]
		x_slope.append(current_slope[0])
		y_slope.append(current_slope[1])
		
		x_sky.append(sky[0])
		y_sky.append(sky[1])

	# Draw the figure
	fig = go.Figure()

	fig.add_trace(go.Scatter(
		x=x_sky, y=y_sky,
		fill='toself',
		mode='lines',
		fillcolor='lightblue',
		name='Sky',
		showlegend=False
	))

	fig.add_trace(go.Scatter(
		x=x_slope, y=y_slope,
		fill='toself',
		mode='lines',
		line=dict(color='saddlebrown'),
		fillcolor='sandybrown',
		name='Slope',
		showlegend=False
	))

	fig.update_layout(
		width=500,
		height=500,
		margin=dict(l=0, r=0, b=0, t=0, pad=0),
		yaxis=dict(
			scaleanchor="x",
			scaleratio=1,
		)
	)


	# Remove axes and grids
	fig.update_xaxes(visible=False, range=[0, x_max])
	fig.update_yaxes(visible=False, range=[0, x_max])
	
	return fig


# Retrieve and update data
def update():
    
	# State variables
	if 'height' not in st.session_state:
		st.session_state.height = 10

	if 'ratio' not in st.session_state:
		st.session_state.ratio = '1:1'
		
	if 'weight' not in st.session_state:
		st.session_state.weight = 18
		
	slope_ratio = int(st.session_state.ratio[-1])
	# Class to interact with database
	db = database()

	# db query
	query = """
			SELECT cohesion, friction, fs 
			FROM results
			WHERE height = :height AND
			length = :length AND
			weight = :weight
			"""

	# Get data
	df = pd.read_sql_query(query, db.conn, params={'height': st.session_state.height, 'length': st.session_state.height*slope_ratio, 'weight': st.session_state.weight})

	# Transform it into matrix 
	df_pivot = pd.pivot_table(df, values='fs', index='cohesion', columns='friction')
	df_pivot = df_pivot[~(df_pivot == 2).all(axis=1)]
	df_pivot = df_pivot.loc[:, ~(df_pivot == 2).all(axis=0)]
	df_text = df_pivot.map(lambda x: f"{x:.2f}")
	df_text = df_text.replace('2.00', ">2")

	# Heatmap
	fig_heatmap = go.Figure(
		data=go.Heatmap(
			z=df_pivot,
			colorscale='RdYlGn',
			zmin=0,
			zmax=2,
			text=df_text,
			texttemplate="%{text}",
			textfont={"size":12},
			hovertemplate="<b>Friction Angle:</b> %{x} <br><b>Cohesion:</b> %{y} <br><b>Safety Factor:</b> %{z:.2f}<extra></extra>"
		)
	)

	fig_heatmap.update_layout(
		xaxis_title='Friction Angle (°)',
		margin=dict(l=0, r=0, b=0, t=0, pad=0),
		yaxis=dict(
			title='Cohesion (kPa)'
		),
		height=len(df_pivot) * 25
	)
	
	st.session_state['fig_heatmap'] = fig_heatmap

	st.session_state['fig_slope'] = get_slope_fig(st.session_state.height, slope_ratio)


update()

# Configure page to wide mode
st.set_page_config(layout="wide")

# Title
st.markdown('# Slope Stability Matrix')

# Inputs
col1, col2, col3 = st.columns([.45, .1, .45], gap='large')
with col1:
	st.markdown(
	"""
		This dashboard shows how the safety factor of different slopes varies as cohesion and friction angle range from 0 to 40, using the Bishop method.\n
		The goal of this application is to be a quick source for those in the early stages of designing slopes. So you don't have to borrow your company's only Slide/GeoStudio license.\n  
		Select the slope height, geometry, and unit weight. The heatmap will show the safety factors for each combination of cohesion and friction angle, helping you quickly assess the stability of the chosen configuration.\n
		If you're a dev and don't give a ***dam*** about soil resistance (pun intended), you might be interested in **[how I built this dashboard](https://github.com/marcuszucareli/slope-variance-study).**
	"""
	)			
	st.radio('Height (m)', [5, 10, 15], index=0, on_change=update, key='height', horizontal=True)
	st.radio('Slope Ratio V:H', ['1:1', '1:2', '1:3'], index=0, on_change=update, key='ratio', horizontal=True)
	st.slider('Weight (kN/m³)', min_value=15, max_value=24, on_change=update, key='weight')
with col2:
	pass
with col3:	
	st.plotly_chart(st.session_state.fig_slope, config={'displayModeBar': False}, use_container_width=False)
	# st.session_state.fig_slope
st.markdown('---')
# Heatmap
st.markdown(f'# Matrix for {st.session_state.height} m slope with ratio of {st.session_state.ratio} and unit weight of {st.session_state.weight} kN/m³')			
st.plotly_chart(st.session_state.fig_heatmap, config={'displayModeBar': False})

# Notes and assumptions
col1, col2 = st.columns(2)
with col1:
	st.markdown(
	"""
		# Notes and Assumptions
		1. This matrix assumes a one-material slope design.
		2. The slope stability method used is [Bishop](https://www.geoengineer.org/education/slope-stability/slope-stability-the-bishop-method-of-slices).
		3. The calculations where made using the Python package [Pyslope](https://github.com/JesseBonanno/PySlope).
		4. To reduce computation time, safety factors greater than 2 were not calculated. This decision was based on the assumption that increasing cohesion or friction angle will always lead to a higher safety factor. Whenever the safety factor reached 2, the remaining values in that row were set to "> 2".
		5. This is an *open source* initiative under the [MIT License](https://github.com/marcuszucareli/slope-variance-study?tab=MIT-1-ov-file), source code available [here](https://github.com/marcuszucareli/slope-variance-study).
		6. If you are a Geotechnical Engineer or a Geologist my [borehole log drawing tool](https://github.com/marcuszucareli/borehole_log_draw) might be usefull for you.
	""")

# Break section
st.markdown('---')

# About the autor
col1, col2, col3 = st.columns([.25,.25,.5], gap='large')
with col1:
	st.image('./assets/Marcus_zucareli_Photo.jpg', width=400)	
with col2:
	st.markdown(
	"""
	# About the autor
	Hi! My name is ***Marcus Zucareli***,\n
	I'm a Civil Engineer passionate about programming and Data Science.\n
	I've been working for 2 years as a Developer and Costumer Onboarding Analyst at [Sentnel](https://www.sentnel.com.br/en?gad_source=1&gclid=Cj0KCQjwkN--BhDkARIsAD_mnIqXhEj9xS6A3Xr28VeQ3sMpipJ_qd_CGZ6ieyrw7_zzE9gguP3J1XIaAq5cEALw_wcB). \n
	I also worked for 3 years as a Geothecnical Consulting Engineer in the mining field for [STATUM](https://statum.eng.br/).
	""")
with col3:
	st.markdown(
	"""
	# Reach me
	🌐 [Linkedin](https://www.linkedin.com/in/marcus-zucareli/?locale=en_US)\n
	💻 [GitHub](https://github.com/marcuszucareli)\n
	📱 [WhatsApp](https://wa.me/33745153017)\n
	✉️ [papaulozucareli@gmail.com](mailto:papaulozucareli@gmail.com)\n
	📞 +33 7 45 15 30 17
	""")

# Variáveis com arquivos
bucket_name = 'mba-senai-alvaro-bucket'
station_file = 'gs://' + bucket_name + '/csv/201508_station_data.csv'
trips_file = 'gs://' + bucket_name + '/csv/201508_trip_data.csv'

# Carrega arquivo CSV
station_df = spark.read.csv(station_file, inferSchema=True, header=True)
station_df.show()
station_df.printSchema()

# Visualizando os dados
station_df.columns
station_df.count()
station_df.describe('dockcount').show()

# Alguns operadores
station_df.filter((station_df.landmark == 'San Jose') | (
    station_df.landmark == 'Redwood City')).show()
station_df.filter(station_df.landmark == 'San Jose').count()
station_df.groupby('landmark').count().show()

# Usando SparkSQL
station_df.registerTempTable('station')
sqlContext.sql('select * from station').show()
sqlContext.sql('select distinct(landmark) from station').show()

# Carregando outro dataframe
trips_df = spark.read.csv(trips_file, inferSchema=True, header=True)
trips_df.registerTempTable('trips')

sqlContext.sql('select avg(duration) from trips').show()
sqlContext.sql('select avg(duration/60) from trips').show()

# Unindo dataframes com SQL

# Cidades que mais tiveram viagens iniciadas
sqlContext.sql('''
select s.landmark, count(*) as qtde
from trips t
  inner join station s
    on s.station_id = t.`Start Terminal`
group by s.landmark
order by qtde desc
''').show()

# Quantas viagens iniciaram em uma cidade e terminaram em outra ?
sqlContext.sql('''
select count(*) as qtde
from trips t
  inner join station s_start
    on s_start.station_id = t.`Start Terminal`
  inner join station s_end
    on s_start.station_id = t.`End Terminal`
where s_start.landmark <> s_end.landmark
''').show()

# Mais detalhes
sqlContext.sql('''
select 
  s_start.landmark as start, 
  s_end.landmark as end, 
  avg(t.duration/60) as avg_duration,
  count(*) as qtde
from trips t
  inner join station s_start
    on s_start.station_id = t.`Start Terminal`
  inner join station s_end
    on s_start.station_id = t.`End Terminal`
where s_start.landmark <> s_end.landmark
group by start,end
order by qtde desc
''').show()

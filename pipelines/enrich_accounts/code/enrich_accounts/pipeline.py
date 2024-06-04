from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from enrich_accounts.config.ConfigStore import *
from enrich_accounts.udfs.UDFs import *
from prophecy.utils import *
from enrich_accounts.graph import *

def pipeline(spark: SparkSession) -> None:
    df_salesforce_Opportunity = salesforce_Opportunity(spark)
    df_Select_Fields = Select_Fields(spark, df_salesforce_Opportunity)
    df_salesforce_Account = salesforce_Account(spark)
    df_Aggregate_by_account = Aggregate_by_account(spark, df_Select_Fields)
    df_Join_byacccountid = Join_byacccountid(spark, df_salesforce_Account, df_Aggregate_by_account)
    enriched_accounts(spark, df_Join_byacccountid)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("enrich_accounts")\
                .getOrCreate()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/enrich_accounts")
    registerUDFs(spark)
    
    MetricsCollector.instrument(spark = spark, pipelineId = "pipelines/enrich_accounts", config = Config)(pipeline)

if __name__ == "__main__":
    main()

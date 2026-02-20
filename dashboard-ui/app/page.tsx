'use client'

import Image from "next/image";
import SparkAccount from "./sparkAccount";
import APForm from "./apForm";

import { DashboardRequest, DashboardRequestStatus, UserInfo } from "@/types/types"
import useSWR from "swr"
import APNotice from "./apNotice";
import { useEffect, useState } from "react";
import Header from "./header";
import APStatus from "./apStatus";
import { getAPIUrl } from "./util";

const fetcher = (input: string) => fetch(input).then((res) => res.json())



export default function Home() {
  const { data, error, isLoading } = useSWR<UserInfo>(getAPIUrl(), fetcher)

  const [currentData, setCurrentData] = useState<UserInfo | undefined>(undefined);
  useEffect(() => {
    if (data) {
      setCurrentData(data);
    }
  }, [data]);

  return (
    <div className="flex flex-col min-h-screen items-center justify-center bg-zinc-50 font-sans ">
      <Header />
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-16 px-16 mb-4 bg-white sm:items-start rounded-md">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold leading-10 tracking-tight text-black mb-2">
              Personal Access Point - Getting Started
            </h1>
            <p className="text-md text-gray-600">
              {currentData && currentData.dashboard_request_status === DashboardRequestStatus.COMPLETE ?
                <span>
                  Your personal AP has been provisioned by the Infrasturcture Services Team. Check the health of
                  your AP below.
                </span>  
                :
                <span>
                  A Personal AP is a dedicated container environment you can use to manage your HTCondor workloads. 
                  Before running your first HTCondor job, please ensure that you've registered for a user account with CHTC,
                  requested access to our Spark Slurm cluster, and let us know 
                  about your project's resource requirements.
                </span>  
              }
            </p>
          </div>
          <div className="max-w-2xl mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Spark Cluster Access
            </h2>
            <SparkAccount data={currentData} error={error} isLoading={isLoading}/>
          </div>
          <div className="max-w-2xl mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Personal AP Configuration
            </h2>
            <APNotice data={currentData} isLoading={isLoading}/>

            {currentData && 
              currentData.chtc_account.spark_account == DashboardRequestStatus.COMPLETE && 
              currentData.dashboard_request_status !== DashboardRequestStatus.COMPLETE &&
              <APForm 
                data={currentData} 
                onSubmit={(newData)=>setCurrentData({
                  ...currentData,
                  dashboard_request_status: DashboardRequestStatus.REQUEST_RECEIVED,
                  dashboard_request_info: newData,
                })}
                onCancel={()=>setCurrentData({
                  ...currentData,
                  dashboard_request_status: DashboardRequestStatus.NOT_REQUESTED,
                  dashboard_request_info: undefined,
                })}
              />
            }

            {currentData && currentData.dashboard_request_status === DashboardRequestStatus.COMPLETE &&
              <APStatus data={currentData} />
            }
          </div>
        </div>
      </main>
    </div>
  );
}

'use client'

import Image from "next/image";
import SparkAccount from "./spark-account";
import APForm from "./apForm";

import { DashboardRequestStatus, UserInfo } from "@/types/types"
import useSWR from "swr"
import APNotice from "./apNotice";

const fetcher = (input: string) => fetch(input).then((res) => res.json() as Promise<UserInfo>)

export default function Home() {
  const { data, error, isLoading } = useSWR('http://localhost:5000/api/', fetcher)
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans ">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white sm:items-start">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold leading-10 tracking-tight text-black">
              Personal Access Point - Getting Started
            </h1>
            <p className="text-md text-gray-600">
              {data && data.dashboard_status === DashboardRequestStatus.COMPLETE ?
                "" :
                <span>
                  Before running your first HTCondor job on a Personal AP, you must
                  create an account on CHTC's Slurm cluster and let us know about 
                  the resource requirements for your AP.
                </span>  
              }
            </p>
          </div>
          <div className="max-w-2xl mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Spark Cluster Access
            </h2>
            <SparkAccount data={data} error={error} isLoading={isLoading}/>
          </div>
          <div className="max-w-2xl mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Personal AP Configuration
            </h2>
            <APNotice data={data} isLoading={isLoading}/>

            {data && data.ldap_authorized && data.dashboard_status !== DashboardRequestStatus.COMPLETE &&
              <APForm data={data}/>
            }

            {data && data.dashboard_status === DashboardRequestStatus.COMPLETE &&
              <p>TODO: Live Dashboard</p>
            }
          </div>
        </div>
      </main>
    </div>
  );
}

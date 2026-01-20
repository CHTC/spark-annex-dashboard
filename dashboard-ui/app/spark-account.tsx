'use client'

import { UserInfo } from "@/types/types"

interface SparkAccountProps {
  error: any;
  isLoading: boolean;
  data: UserInfo | undefined;
}

/**
 * Widget to display a user's Spark account information
 * based on a query to the dashboard API.
 */
export default function SparkAccount({data, error, isLoading}: SparkAccountProps) {
  return  (
    <p className="text-md text-gray-600">
      {(()=>{
        if (isLoading) return <span>Loading Spark account information...</span>
        if (error) return <span>Error loading Spark account information.</span>
        if (!data) return <span>No Spark account information available.</span>
        if (!data.ldap_authorized) {
          return (
            <span>
              No Spark access has been configured for user {data.user_id}. Please
              {" "}
              <a className="text-blue-600 hover:text-blue-700" href="https://chtc.wisc.edu/uw-research-computing/form.html">request an account</a> 
              {" "}
              from CHTC.
            </span>)
        }

        return (
          <span>
            Spark access is active for user {data.user_id}.
          </span>)

      })()}
    </p>
  )

}

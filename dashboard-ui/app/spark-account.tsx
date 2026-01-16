'use client'

import useSWR from "swr"

const fetcher = (input: string) => fetch(input).then((res) => res.json())

/**
 * Widget to display a user's Spark account information
 * based on a query to the dashboard API.
 */
export default function SparkAccount() {

  const { data, error, isLoading } = useSWR('http://localhost:5000/api/', fetcher)

  if (isLoading) return <div>Loading Spark account information...</div>
  if (error) return <div>Error loading Spark account information.</div>
  if (!data) return <div>No Spark account information available.</div>

  return <div>Loaded Spark account information! Yay.</div>

}

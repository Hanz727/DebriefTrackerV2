import React, {useState} from "react";
import Filters from "./Filters";
import Table from "./Table";
import Stats from "./Stats";

const Body = () => {
    const [forceUpdateState, forceUpdate] = useState(false)
    const [data, setData] = useState([]);

    const handleRefresh = () => {
        forceUpdate(!forceUpdateState);
    }

    return (
        <div>
            <Filters refreshFunc={handleRefresh}/>
            <Stats data={data}/>
            <Table updateState={forceUpdateState} data={data} setData={setData}/>

        </div>
    )
}

export default Body
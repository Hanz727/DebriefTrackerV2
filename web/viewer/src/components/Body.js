import React, {useState} from "react";
import Filters from "./Filters";
import Table from "./Table";

const Body = () => {
    const [forceUpdateState, forceUpdate] = useState(false)

    const handleRefresh = () => {
        forceUpdate(!forceUpdateState);
    }

    return (
        <div>
            <Filters refreshFunc={handleRefresh}/>
            <Table updateState={forceUpdateState.toString()}/>

        </div>
    )
}

export default Body
import React from "react";
import '../StatsBox.css'

const StatsBox = ({title, children}) => {
    return (
        <div className="StatsBox">
            <h4>{title}</h4>
            <hr/>
            {children}
        </div>
        )
}

export default StatsBox
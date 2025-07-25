import React from "react";
import '../StatsBox.css'

const StatsBox = ({title, children, style}) => {
    return (
        <div className="StatsBox" style={style}>
            <h4>{title}</h4>
            <div className="Divider"></div>
            {children}
        </div>
        )
}

export default StatsBox
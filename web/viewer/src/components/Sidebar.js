import React from "react";
import '../Sidebar.css'

const Sidebar = () => {
    return (
        <div className="sidebar">
            <a href="/" className="nav-link">HOME</a>
            <a href="/reports" className="nav-link">AP STRIKE REPORTS</a>
            <a href="#" className="nav-link">DATA VIEWER</a>
            <a href="/tacview" className="nav-link">TACVIEW</a>
            <a href="/tracks" className="nav-link">REPLAYS</a>
        </div>
    )
}

export default Sidebar
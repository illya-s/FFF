import './Base.css'
import Header from "./base/Header.jsx"

import './Theme.css'
import './pages/media/List.css'

import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import RouteProgress from "./RouteProgress.jsx";

import LR from './pages/user/LR.jsx'
import Logout from "./pages/user/Logout.jsx";


function Auth() {
    return (
        <>
            <RouteProgress/>

            <Header/>
            <main className="auth-main">
                <Routes>
                    <Route path="/lr" element={<LR />} />
                    <Route path="/logout" element={<Logout />} />
                </Routes>
            </main>
        </>
    )
}

export default Auth;
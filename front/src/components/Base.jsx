import './Base.css'
import Header from "./base/Header.jsx"
import Aside from "./base/Aside.jsx";

import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

import './Theme.css'
import './pages/media/List.css'
import {useState} from "react";
import RouteProgress from "./RouteProgress.jsx";
import Media from "./pages/media/Media.jsx";
import MediaStatus from "./pages/profile/MediaStatus.jsx";
import Legal from "./pages/support/Legal.jsx";
import SupportForm from "./pages/support/SupportForm.jsx";
import Profile from "./pages/profile/Profile.jsx";
import History from "./pages/profile/History.jsx";
import Rated from "./pages/profile/Rated.jsx";

function Base() {
	const [isAsideOpen, setIsAsideOpen] = useState(false);

	const handleAside = () => {
		setIsAsideOpen(prev => !prev);
	};

	return (
		<>
			<RouteProgress/>

			<Header handleAside={handleAside}/>
			<main className="base-main">
				<Aside isOpen={isAsideOpen} setIsOpen={setIsAsideOpen} />
				<div className="content">
					<Routes>
						<Route path="watch/:hash" element={<Media />} />

						<Route path="profile/media_status/:status" element={<MediaStatus />} />
						<Route path="profile/" element={<Profile />} />
						<Route path="profile/history/" element={<History />} />
						<Route path="profile/rated/" element={<Rated />} />

						<Route path="support/legal/" element={<Legal />} />
						<Route path="support/form/" element={<SupportForm />} />
					</Routes>
				</div>
			</main>
		</>
	)
}

export default Base
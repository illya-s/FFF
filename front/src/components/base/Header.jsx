import './Header.css'
import {
	Logo,
	Burger,
	Search,
	Back,
	User,
	ArrowDown,
	NoPoster,
	Settings,
	History,
	Star,
	Chat, Legal, SignIn, SignOut, Loading, ArrowLeft
} from '../../icons/icons.jsx'
import { DownOutlined } from '@ant-design/icons';
import {AutoComplete, Dropdown, Space, Input, Avatar, Button} from 'antd';
import axios from "axios";
import {useEffect, useRef, useState} from "react";
import {debounce} from "lodash";

import { useContext } from "react";
import { UserContext } from "../../UserContext";
import { serverUrl } from '../Config.jsx'

import { useMessageApi } from "../../MessageProvider";
import {Link} from "react-router-dom";


function Header({ handleAside }) {
	const user = useContext(UserContext);
	const messageApi = useMessageApi();

	const [state, setState] = useState('enter') // enter, search, result, empty
	const [results, setResults] = useState([]);
	const [isSearchOpen, setIsSearchOpen] = useState(false);
	const isSearchOpenRef = useRef(isSearchOpen);


	const messageErrorLogin = () => {
		messageApi.error("Войдите в акаунт!")
	}


	const items = [
		{
			label: (
				<a href={user && "/profile/"} onClick={!user ? messageErrorLogin : undefined}>Профиль</a>
			),
			icon: <Settings style={{ width: '25px', height: 'auto' }}/>,
			key: '0',
		},
		{
			label: (
				<a href={user && "/profile/history/"} onClick={!user ? messageErrorLogin : undefined}>История</a>
			),
			icon: <History style={{ width: '25px', height: 'auto' }}/>,
			key: '1',
		},
		{
			label: (
				<a href={user && "/profile/rated/"} onClick={!user ? messageErrorLogin : undefined}>Оценённые</a>
			),
			icon: <Star style={{ width: '25px', height: 'auto' }}/>,
			key: '2',
		},
		{
			type: 'divider',
		},
		{
			label: (
				<a href="/support/form/">Поддержка</a>
			),
			icon: <Chat style={{ width: '25px', height: 'auto' }}/>,
			key: '4',
		},
		{
			label: (
				<Link to="/support/legal">Условия и политика</Link>
			),
			icon: <Legal style={{ width: '25px', height: 'auto' }}/>,
			key: '5',
		},
		{
			type: 'divider',
		},
		user ? {
			label: (
				<Link to="/user/logout">Выход</Link>
			),
			icon: <SignOut style={{ width: '25px', height: 'auto' }}/>,
			key: '7',
		} : {
			label: (
				<Link to="/user/lr">Вход</Link>
			),
			icon: <SignIn style={{ width: '25px', height: 'auto' }}/>,
			key: '7',
		},
	];

	useEffect(() => {
		isSearchOpenRef.current = isSearchOpen;
	}, [isSearchOpen]);

	const handleInput = debounce((value) => {
		if (value.length < 3) {
			setResults([])
			setState('enter')
			return
		}

		setIsSearchOpen(true);
		setState('search')

		axios.get('http://127.0.0.1:8080/api/search/auto/', {
			params: {q: value}
		})
			.then(response => {
				const results = response.data.results;
				setResults(results);
				if ((results.length !== 0)) {
					setState("result")
				} else {
					setState("empty")
				}
			})
			.catch(error => {
				console.error('Ошибка при запросе:', error);
			});
	}, 300)

	const handleSearch = (value) => {
		if (value.length < 3) return

		console.log(value);
	};

	const showSearch = () => {
		setIsSearchOpen(true);
	};
	const handleKey = (e) => {
		if (e.key === 'Enter') {
			handleSearch(e)
		} else if (e.key === 'Escape') {
			e.target.blur()
			setIsSearchOpen(false);
		}
	}

	useEffect(() => {
		const handleClickOutside = (e) => {
			if (!e.target.closest('.header-search-wrapper') && isSearchOpenRef.current) {
				setIsSearchOpen(false);
			}
		};

		document.addEventListener('click', handleClickOutside)
	}, []);

	return (
		<header>
			<div className="header-logo-wrapper">
				<button
					className="header-logo-toggle-aside"
					onClick={handleAside}
				>
					<Burger/>
				</button>

				<a className="header-logo" href="/">
					<Logo/>
					<span>SarangDorama</span>
				</a>
			</div>

			<div className="header-search-wrapper">
				<div className="header-search">
					<Button
						className="header-search-button-back"
						icon={<ArrowLeft />}
						onClick={() => setIsSearchOpen(false)}
					></Button>
					<input
						className="header-search-input"
						type="text"
						onInput={(e) => handleInput(e.target.value)}
						onFocus={showSearch}
						onKeyDown={handleKey}
						placeholder="Введите запрос..."
						name=""
						id="headerSearchInput"
					/>
					<Button
						className="header-search-button-search"
						icon={<Search/>}
						onClick={() => handleSearch(document.getElementById('headerSearchInput').value)}
					></Button>
				</div>

				<div className={isSearchOpen ? "search-autocomplete active" : "search-autocomplete"}>
					{state === 'enter' && <p className="autocomplete-no-results">Введитье запрос (минимум 3 символа)!</p>}
					{state === 'search' && <Loading style={{width:'50px', height:'max-content', 'alignSelf':'center'}} />}
					{state === 'empty' && <p className="autocomplete-no-results">Ничего не найдено!</p>}
					{state === 'result' && (
						results.map(media => (
							<a key={media.hash} href={``} className="autocomplete-block">
								{media.poster ? (
									<img className="autocomplete-poster" src={media.poster} loading="lazy"
										 alt={media.name}/>
								) : (
									<div className="autocomplete-no-poster">
										<NoPoster/>
									</div>
								)}

								<span className="autocomplete-title">{media.name}</span>

								<div className="autocomplete-info">
									<p>{media.year}</p>
									<span>|</span>
									<p>{media.country}</p>
								</div>
							</a>
						))
					)}
				</div>
			</div>

			<Dropdown
				menu={{items}}
				trigger={['click']}
				placement="bottomRight"
			>
				<a className="header-user-btn" onClick={e => e.preventDefault()}>
					<Space>
						{!user ? (
							<Avatar icon={<User style={{ width: '25px', height: 'auto' }}/>}></Avatar>
						) : (
							user.avatar ? (
								<Avatar src={serverUrl + user.avatar}></Avatar>
							) : (
								<Avatar>{user.username && (user.username[0])}</Avatar>
							)
						)}
						<DownOutlined />
					</Space>
				</a>
			</Dropdown>
		</header>
)
}

export default Header
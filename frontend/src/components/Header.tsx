import { useState } from 'react'
//import { useNavigate } from 'react-router-dom'
import HamburgerMenu from './HamburgerMenu'

const Header = () => {
  //const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <>
      <header className="fixed top-0 left-0 w-full flex justify-between p-4 bg-white shadow-md z-50">
        <div className="font-bold text-xl text-gray-700">InsightFlow AI</div>
        <button onClick={toggleMenu} className="text-3xl">☰</button>
        <HamburgerMenu isOpen={isMenuOpen} toggleMenu={toggleMenu} />
      </header>
      {/* Spacer to prevent content from hiding under the fixed header */}
      <div className="h-16 w-full"></div>
    </>
  )
}

export default Header

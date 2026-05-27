import { useState, useEffect, useRef } from "react"

export function useResumeMenu() {
  const [activeMenuId, setActiveMenuId] = useState(null)
  const menuRefs = useRef({})

  const toggleMenu = (id) => {
    setActiveMenuId((prev) => (prev === id ? null : id))
  }

  const closeMenu = () => {
    setActiveMenuId(null)
  }

  // Handle click outside to close the active menu
  useEffect(() => {
    function handleClickOutside(event) {
      if (activeMenuId) {
        const currentRef = menuRefs.current[activeMenuId]
        if (currentRef && !currentRef.contains(event.target)) {
          setActiveMenuId(null)
        }
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [activeMenuId])

  const registerRef = (id, el) => {
    if (el) {
      menuRefs.current[id] = el
    } else {
      delete menuRefs.current[id]
    }
  }

  return {
    activeMenuId,
    toggleMenu,
    closeMenu,
    registerRef
  }
}

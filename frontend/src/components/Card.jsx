import { motion } from "framer-motion"


function Card(props) {
  return (
    <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        
    className="
        bg-white/5
        backdrop-blur-lg
        border
        border-white/10
        p-6
        rounded-2xl
        hover:scale-105
        hover:border-blue-500/40
        transition-all
        duration-300
        shadow-xl
    ">

      <h2 className="text-gray-400">
        {props.title}
      </h2>

      <p className="text-4xl font-bold mt-2">
        {props.value}
      </p>

    </motion.div>
  )
}

export default Card
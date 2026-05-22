function Card(props) {
  return (
    <div className="
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

    </div>
  )
}

export default Card
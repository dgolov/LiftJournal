/**
 * @typedef {Object} ExerciseDefinition
 * @property {string}   id
 * @property {string}   name
 * @property {string}   muscleGroup
 * @property {string[]} secondaryMuscles
 * @property {string}   equipment
 * @property {string}   description
 * @property {boolean}  isCustom
 */

/**
 * @typedef {Object} WorkoutSet
 * @property {string}  id
 * @property {number}  weight       - kg
 * @property {number}  reps
 * @property {boolean} completed
 * @property {number}  [rpe]        - 1-10
 */

/**
 * @typedef {Object} WorkoutExercise
 * @property {string}       exerciseId
 * @property {string}       exerciseName
 * @property {WorkoutSet[]} sets
 * @property {string}       [notes]
 */

/**
 * @typedef {Object} Workout
 * @property {string}            id
 * @property {string}            date          - 'YYYY-MM-DD'
 * @property {string}            type
 * @property {string}            title
 * @property {number}            durationMinutes
 * @property {string}            [notes]
 * @property {WorkoutExercise[]} exercises
 * @property {number}            createdAt     - epoch ms
 */

/**
 * @typedef {Object} WeightEntry
 * @property {string} date  - 'YYYY-MM-DD'
 * @property {number} kg
 */

/**
 * @typedef {Object} Goal
 * @property {string}  id
 * @property {string}  text
 * @property {string}  targetDate  - 'YYYY-MM-DD'
 * @property {boolean} done
 */

/**
 * @typedef {Object} User
 * @property {string}        name
 * @property {number}        age
 * @property {string|null}   avatarUrl
 * @property {WeightEntry[]} weightLog
 * @property {Goal[]}        goals
 */

import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import { API_PATH } from '../config'

const styles = theme => ({
  root: {
  }
})

class PostViewer extends React.Component {
  state = {
    post: {
      id: -1,
      title: '',
      description: '',
      content: ''
    }
  }

  componentDidMount () {
    const { match } = this.props
    const url = `${API_PATH}/${match.params.id}`
    fetch(url)
      .then(response => {
        if (response.ok) {
          response.json()
            .then(post => {
              this.setState({ post })
            })
            .catch(error => {
              console.log(error)
            })
        }
      })
      .catch(error => {
        console.log(error)
      })
  }

  render () {
    const { classes } = this.props
    const { post } = this.state

    return (
      <div className={classes.root}>
        <h2>{post.title}</h2>
        <h4>{post.description}</h4>
        <p>{post.content}</p>
      </div>
    )
  }
}

PostViewer.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired
}

export default withStyles(styles)(PostViewer)

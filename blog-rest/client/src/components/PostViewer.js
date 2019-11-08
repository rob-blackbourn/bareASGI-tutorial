import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import IconButton from '@material-ui/core/IconButton'
import HomeIcon from '@material-ui/icons/Home'
import LinkRef from './LinkRef'
import Grid from '@material-ui/core/Grid'
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
      <Grid container className={classes.root}>
        <Grid item xs={12}>
          <Typography variant='h2' gutterBottom>{post.title}</Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography variant='h4' gutterBottom>{post.description}</Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography variant='body1'>{post.content}</Typography>
        </Grid>
        <Grid item xs={10} />
        <Grid item xs={2}>
          <IconButton edge='end' aria-label='edit' component={LinkRef} to='/index'>
            <HomeIcon />
          </IconButton>
        </Grid>
      </Grid>
    )
  }
}

PostViewer.apply.propTypes = {
  classes: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired
}

export default withStyles(styles)(PostViewer)

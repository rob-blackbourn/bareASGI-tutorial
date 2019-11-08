import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from '@material-ui/core/styles'
import Grid from '@material-ui/core/Grid'
import TextField from '@material-ui/core/TextField'
import IconButton from '@material-ui/core/IconButton'
import SaveIcon from '@material-ui/icons/Save'
import HomeIcon from '@material-ui/icons/Home'
import LinkRef from './LinkRef'

const styles = theme => ({
  root: {},
  titleTextField: {
    width: 400
  },
  descriptionTextField: {
    width: 400
  },
  contentTextField: {
    width: 400
  },
  submitButton: {
    margin: theme.spacing(2)
  }
})

const PostEditor = props => {
  const {
    classes,
    title,
    onTitleChange,
    description,
    onDescriptionChange,
    content,
    onContentChange,
    onSubmit
  } = props

  return (
    <div className={classes.root}>
      <Grid container>
        <Grid item xs={12}>
          <TextField
            className={classes.titleTextField}
            label='Title'
            value={title}
            onChange={event => onTitleChange(event.target.value)}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            className={classes.descriptionTextField}
            label='Description'
            value={description}
            onChange={event => onDescriptionChange(event.target.value)}
            multiline
            rows={2}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            className={classes.contentTextField}
            label='Content'
            value={content}
            onChange={event => onContentChange(event.target.value)}
            multiline
            rows={20}
          />
        </Grid>
        <Grid item xs={1}>
          <IconButton edge='end' aria-label='edit' component={LinkRef} to='/index'>
            <HomeIcon />
          </IconButton>
        </Grid>
        <Grid item xs={10} />
        <Grid item xs={1}>
          <IconButton edge='end' aria-label='delete' onClick={onSubmit}>
            <SaveIcon />
          </IconButton>
        </Grid>
      </Grid>
    </div>
  )
}

PostEditor.propTypes = {
  classes: PropTypes.object.isRequired,
  title: PropTypes.string,
  onTitleChange: PropTypes.func.isRequired,
  description: PropTypes.string,
  onDescriptionChange: PropTypes.func.isRequired,
  content: PropTypes.string,
  onContentChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default withStyles(styles)(PostEditor)
